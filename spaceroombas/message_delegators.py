from data.messages import MapUpdateRequestMessage, NewConnectionMessage, PlayerFirmwareChange
from data.state import PlayerExistsError

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