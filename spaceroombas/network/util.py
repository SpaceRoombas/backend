from .serialization import create_carrier_pigeon, message_types
from .flats.message_type import message_type

immediates = [
    message_type.ACK,
    message_type.Handshake,
]

def utility_create_message_connectionACK():
    return create_carrier_pigeon("connect", None, message_types["ACK"])

def utility_create_message_recieveACK():
    return create_carrier_pigeon("recieve", None, message_types["ACK"])

def utility_create_message_handshakeACK():
    return create_carrier_pigeon("handshake", None, message_types["ACK"])

"""
Checks if message requires immediate service
"""
def is_immediate(carrier):
    return carrier.type in immediates
