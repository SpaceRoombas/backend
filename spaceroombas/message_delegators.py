from typing import List
from data import messages
from data.state import GameState, PlayerExistsError, RobotMoveEvent, RobotErrorEvent
import logging

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

    def delegate(self, messageWrapper, game_state: GameState, network):
        # Verify that we have a player in game state
        # Send map for player location

        message = messageWrapper.message
        robots = None

        try:
            game_state.add_player(message.client_id)
        except PlayerExistsError:
            logging.info("Got orphaned player: %s" % (message.client_id))
            # Send robots. This happens on new players, because the creation
            # of their first robot will trigger a list send.
            # In which, we want EVERYONE to know
            robots = game_state.get_all_robots()
            if len(robots) > 0:
                network.enque_message(messageWrapper.client,
                                      messages.RobotListingMessage(robots))

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
            for k, v in robot.items():
                # At this point, this should be a robot object
                try:
                    v.set_firmware(message.code)
                except:
                    err = f"Robot {player}:{v.robot_id} had syntax error"
                    logging.info(err)
                    self.add_robot_error(game_state, player, v.robot_id)
                    break
        else:
            robot = game_state.get_robot(player, robot_id)
            try:
                robot.set_firmware(message.code)
            except:
                err = f"Robot {player}:{robot_id} had syntax error"
                logging.info(err)
                self.add_robot_error(game_state, player, robot_id, err)

        logging.debug("Applied firmware change for \"%s:%s\"" %
                      (player, robot_id))

    def add_robot_error(self, game_state, player_id, robot_id, err):
        player = game_state.players[player_id]
        player.add_state_change_event(
            RobotErrorEvent(player_id, robot_id, err))


delegators = {
    messages.MapUpdateRequestMessage: MapUpdateRequestMessageDelegator(),
    messages.NewConnectionMessage: NewConnectionDelegator(),
    messages.PlayerFirmwareChange: PlayerFirmwareChangeDelegator(),
}


def delegate_client_message(messageWrapper, game_state, network):
    msg_type = type(messageWrapper.message)

    try:
        delegator = delegators[msg_type]
    except KeyError:
        logging.info(
            "Failed delegating message (do not have a handler for that message)")
        return

    delegator.delegate(messageWrapper, game_state, network)


# ---------------------------
#
# Server Message Delegation
#
# ---------------------------


class RobotMoveEventDelegator():
    def delegate(self, network, event):
        network_message = messages.PlayerRobotMoveMessage(
            event.player_id, event.robot_id, event.new.x, event.new.y)

        # Bolt on the EntityLocation objects for movement
        network_message.new = event.new
        network_message.old = event.old

        logging.debug("Robot \"%s\":\"%s\" moved: %s -> %s"
                      % (
                          event.player_id,
                          event.robot_id,
                          event.old, event.new
                      ))

        network.enque_message(None, network_message)


class RobotErrorEventDelegator():
    def delegate(self, network, event):
        network_message = messages.PlayerRobotErrorMessage(
            event.player_id, event.robot_id, event.error)
        logging.debug("Robot \"%s\":\"%s\" Errror: %s"
                      % (
                          event.player_id,
                          event.robot_id,
                          event.error
                      ))

        network.enque_message(event.player_id, network_message)


event_delegators = {
    RobotMoveEvent: RobotMoveEventDelegator(),
    RobotErrorEvent: RobotErrorEventDelegator(),
}


def delegate_state_changes(events: list, network):
    delegator = None
    for event in events:
        event_type = type(event)
        try:
            delegator = event_delegators[event_type]
            delegator.delegate(network, event)
        except KeyError:
            logging.info("Cannot send this message out yet")


def delegate_notify_new_robots(game_state: GameState, network):
    robots = game_state.check_for_new_robots()

    if robots is not None:
        network.enque_message(None, messages.RobotListingMessage(robots))


def delegate_server_messages(game_state: GameState, network):
    state_changes = list()

    # Notify on new robots
    delegate_notify_new_robots(game_state, network)

    # Check for player state events
    for player in game_state.players.values():
        state_changes.extend(player.get_list_state_change_events())

    if len(state_changes) > 0:
        delegate_state_changes(state_changes, network)
