from data.messages import MapUpdateRequestMessage

class MessageDelegator:

    def delegate(self, messageWrapper, game_state, network):
        raise NotImplementedError

class MapUpdateRequestMessageDelegator(MessageDelegator):

    def delegate(self, messageWrapper, game_state, network):
        network.enque_message(messageWrapper.client, game_state.map)


delegators = {
    MapUpdateRequestMessage:MapUpdateRequestMessageDelegator()
}

def delegate_client_message(messageWrapper, game_state, network):
    msg_type = type(messageWrapper.message)

    try:
        delegator = delegators[msg_type]
    except KeyError:
        print("Failed delegate message (do not have a handler for that message)")
        return

    delegator.delegate(messageWrapper, game_state, network)