from serialization import create_carrier_pigeon, message_types
import flats.message_type

def utility_create_message_connectionACK():
    return create_carrier_pigeon("connect", None, message_types["ACK"])

def utility_create_message_recieveACK():
    return create_carrier_pigeon("recieve", None, message_types["ACK"])


"""
Checks if message requires immediate service
"""
def is_immediate(carrier):
    message_types = flats.message_type.message_type
    immediates = [
        message_types.ACK,
        message_types.Handshake
    ]

    return carrier.type in immediates
