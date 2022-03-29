from random import shuffle
from data.state import GameState
import client_networking
from twisted.internet.task import LoopingCall
from roombalang.parser import Parser
from roombalang.transpiler import Transpiler
from roombalang.interpreter import Interpreter

import message_delegators

def game_loop(game_state, network):
    
    client_messages = network.fetch_messages()

    # Delegate all messages and apply to game state
    for client_message in client_messages:
        message_delegators.delegate_client_message(client_message, game_state, network)

    for player in shuffle(game_state.players.values()):
        bots = shuffle(player.robots.values())

        for bot in bots:
            up = (lambda:game_state.move_robot_up(player, bot),0)
            down = (lambda:game_state.move_robot_down(player, bot),0)
            left = (lambda:game_state.move_robot_left(player, bot),0)
            right = (lambda:game_state.move_robot_right(player, bot),0)
            fns = {"move_north":up, "move_south":down, "move_west":left, "move_east":right}
            bot.tick(fns)
        

network = client_networking.RoombaNetwork(9001)
game_state = GameState()


print("Starting main loop")
game_looper = LoopingCall(game_loop, game_state, network)
game_looper.start(0.2)

print("Bringing up network")
network.start()


