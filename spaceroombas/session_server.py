from random import shuffle
from data.state import GameState, RobotErrorEvent
import client_networking
from twisted.internet.task import LoopingCall
from roombalang.exceptions import LangException
import logging
import sys
from os import environ
import message_delegators

# Tunables
GAME_LOOP_DELTA = 0.5
NETWORK_UPDATE_DELTA = 0.1

LOGLEVEL = environ.get('LOGGING', 'WARNING').upper()
logging.basicConfig(
    level=LOGLEVEL,
    handlers=[logging.StreamHandler(sys.stdout)],
    format='%(levelname)s: -- %(message)s'
)


def tick_bots(game_state: GameState):
    bots = game_state.get_all_robots()
    shuffle(bots)

    for bot in bots:
        try:
            bot.tick()
        except LangException as e:
            logging.info(f"Player {bot.owner} code had exception: {e}!")
            game_state.players[bot.owner].add_state_change_event(
                RobotErrorEvent(bot.owner, bot.robot_id, e))


def game_loop(game_state: GameState, network):
    client_messages = network.fetch_messages()

    # Delegate all messages and apply to game state
    for client_message in client_messages:
        message_delegators.delegate_client_message(
            client_message, game_state, network)

    # Update game state
    tick_bots(game_state)

    # Send out messages to clients
    message_delegators.delegate_server_messages(game_state, network)


def spin_server(port):
    network = client_networking.RoombaNetwork(port, NETWORK_UPDATE_DELTA)
    game_state = GameState()

    logging.debug("Starting main loop")
    game_looper = LoopingCall(game_loop, game_state, network)
    game_looper.start(GAME_LOOP_DELTA)

    logging.debug("Bringing up network")
    network.start()

    # Server exit
    logging.shutdown()


if __name__ == "__main__":
    port = int(environ.get('PORT', '9001'))
    spin_server(port)
