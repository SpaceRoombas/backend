from random import shuffle
from data.state import GameState
import client_networking
from twisted.internet.task import LoopingCall
from roombalang.parser import Parser
from roombalang.transpiler import Transpiler
from roombalang.interpreter import Interpreter
from roombalang.exceptions import LangException

import message_delegators

GAME_LOOP_DELTA = 0.3
NETWORK_UPDATE_DELTA = 0.1

def game_loop(game_state: GameState, network):
    client_messages = network.fetch_messages()

    # Delegate all messages and apply to game state
    for client_message in client_messages:
        message_delegators.delegate_client_message(client_message, game_state, network)

    bots = []
    for player in game_state.players.values():
        bots += player.robots.values()

    shuffle(bots)

    for bot in bots:
        up = (lambda args: game_state.move_robot_up(bot.owner, bot.robot_id), 0)
        down = (lambda args: game_state.move_robot_down(bot.owner, bot.robot_id), 0)
        left = (lambda args: game_state.move_robot_left(bot.owner, bot.robot_id), 0)
        right = (lambda args: game_state.move_robot_right(bot.owner, bot.robot_id), 0)
        fns = {"move_north": up, "move_south": down, "move_west": left, "move_east": right}
        try:
            bot.tick(fns)
        except LangException as e:
                print(f"Player {bot.owner} code had exception: {e}!")
                
    # Send out messages to clients
    message_delegators.delegate_server_messages(game_state, network)

network = client_networking.RoombaNetwork(9001, NETWORK_UPDATE_DELTA)
game_state = GameState()

print("Starting main loop")
game_looper = LoopingCall(game_loop, game_state, network)
game_looper.start(GAME_LOOP_DELTA)

print("Bringing up network")
network.start()
