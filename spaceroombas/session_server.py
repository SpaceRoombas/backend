from pytest import Session
import client_networking
from map import mapgeneration
from twisted.internet.task import LoopingCall

from data.types import GameMap
import message_delegators


class GameState():
    def __init__(self):
        self.map = None

def game_loop(game_state, network):
    
    client_messages = network.fetch_messages()

    # Delegate all messages
    for client_message in client_messages:
        message_delegators.delegate_client_message(client_message, game_state, network)

network = client_networking.RoombaNetwork(9001)

game_state = GameState()

print("Generating initial map")
game_state.map = GameMap()
game_state.map.land_map = mapgeneration.generate()

print("Starting main loop")
game_looper = LoopingCall(game_loop, game_state, network)
game_looper.start(0.2)

print("Bringing up network")
network.start()
