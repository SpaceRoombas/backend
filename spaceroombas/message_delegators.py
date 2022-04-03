from typing import List
from data.messages import MapUpdateRequestMessage, NewConnectionMessage, PlayerFirmwareChange, PlayerRobotMoveMessage
from data.state import GameState, PlayerExistsError, RobotMoveEvent

# ---------------------------
#
# Client Message Delegation
#
# ---------------------------

class MessageDelegator:

    def delegate(self, messageWrapper, game_state, network):
        raise NotImplementedError

class MapUpdateRequestMessageDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        map_sector = game_state.map.get_sector('0,0')
        network.enque_message(messageWrapper.client, map_sector)

class NewConnectionDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        # Verify that we have a player in game state
        # Send map for player location

        message = messageWrapper.message

        try:
            game_state.add_player(message.client_id)
        except PlayerExistsError:
            # TODO send down current code for EACH robot registered to player
            print("Got orphaned player: %s" % (message.client_id))
        
        # Send a map
        map_sector = game_state.map.get_sector('0,0')
        network.enque_message(messageWrapper.client, map_sector)

class PlayerFirmwareChangeDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        message = messageWrapper.message
        player = messageWrapper.client
        robot_id = message.robot_id
        robot = None

        if robot_id is None:
            # Apply to all player robots
            robot = game_state.get_player_robots(player)
            for k,v in robot.items():
                # At this point, this should be a robot object
                v.set_firmware(message.code)
        else:
            robot = game_state.get_robot(player, robot_id)
            robot.set_firmware(message.code)
        print("Applied firmware change for (%s:%s)" % (player, robot_id))
            

delegators = {
    MapUpdateRequestMessage:MapUpdateRequestMessageDelegator(),
    NewConnectionMessage:NewConnectionDelegator(),
    PlayerFirmwareChange:PlayerFirmwareChangeDelegator(),
}

def delegate_client_message(messageWrapper, game_state, network):
    msg_type = type(messageWrapper.message)

    try:
        delegator = delegators[msg_type]
    except KeyError:
        print("Failed delegating message (do not have a handler for that message)")
        return

    delegator.delegate(messageWrapper, game_state, network)


# ---------------------------
#
# Server Message Delegation
#
# ---------------------------


class RobotMoveEventDelegator():
    def delegate(self, network, event):
        network_message = PlayerRobotMoveMessage(event.player_id, event.robot_id, event.new.x, event.new.y)
        print("Player \"%s\" Robot \"%s\" moved to: %s from: %s" 
        % (
        event.player_id, 
        event.robot_id, 
        event.new, event.old
        ))

        network.enque_message(None, network_message)


event_delegators = {
    RobotMoveEvent:RobotMoveEventDelegator()
}

def delegate_state_changes(events: list, network):
    delegator = None
    for event in events:
        event_type = type(event)
        try:
            delegator = event_delegators[event_type]
            delegator.delegate(network, event)
        except KeyError:
            print("Cannot send this message out yet")

def delegate_server_messages(game_state: GameState, network):
    state_changes = list()
    
    # Check for player state events
    for player in game_state.players.values():
        state_changes.extend(player.get_list_state_change_events())
    
    if len(state_changes) > 0:
        delegate_state_changes(state_changes, network)