from data.messages import MapUpdateRequestMessage, NewConnectionMessage

class MessageDelegator:

    def delegate(self, messageWrapper, game_state, network):
        raise NotImplementedError

class MapUpdateRequestMessageDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        map_sector = game_state.map.get_sector(0)
        network.enque_message(messageWrapper.client, map_sector)

class NewConnectionDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        # Verify that we have a player in game state
        # Send map for player location

        message = messageWrapper.message

        # Send a map
        map_sector = game_state.map.get_sector(0)
        network.enque_message(messageWrapper.client, map_sector)
        game_state.add_player(message.client_id)

        # TODO Send any other inital connection messages here


delegators = {
    MapUpdateRequestMessage:MapUpdateRequestMessageDelegator(),
    NewConnectionMessage:NewConnectionDelegator()
}

def delegate_client_message(messageWrapper, game_state, network):
    msg_type = type(messageWrapper.message)

    try:
        delegator = delegators[msg_type]
    except KeyError:
        print("Failed delegate message (do not have a handler for that message)")
        return

    delegator.delegate(messageWrapper, game_state, network)