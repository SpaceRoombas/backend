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

    # TODO Execute step of interpreters

    # TODO Apply interpreter results to game state

    # TODO Send messages for gamestate changes (and location updates)

network = client_networking.RoombaNetwork(9001)
game_state = GameState()


print("Starting main loop")
game_looper = LoopingCall(game_loop, game_state, network)
game_looper.start(0.2)

print("Bringing up network")
network.start()


