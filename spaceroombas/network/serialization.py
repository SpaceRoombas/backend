from multiprocessing.sharedctypes import Value
from .flats import carrier_pigeon
from .flats.message_type import message_type
from .flats.session_handshake import session_handshake
import flatbuffers
from . import messages

# Maps to the backing flat
message_types = {
    "Message": message_type().Message,
    "ACK": message_type().ACK
}


# Various mappers
class MessageMapper:
    def mapBuffer(self, buffer):
        raise NotImplementedError

    def mapMessage(self, message):
        raise NotImplementedError


class CarrierMapper(MessageMapper):
    def unpack_carrier_payload(self, carrier):
        payloadsz = carrier.PayloadLength()
        payload_buffer = bytearray(payloadsz)

        for i in range(0, payloadsz):
            payload_buffer[i] = carrier.Payload(i)
        return payload_buffer

    def mapBuffer(self, buffer):
        # deserialize
        carrier = carrier_pigeon.carrier_pigeon.GetRootAs(buffer, 0)
        hint = carrier.Hint().decode('utf-8')
        message_type = carrier.Type()
        carrier_payload = None

        if not carrier.PayloadIsNone():
            carrier_payload = self.unpack_carrier_payload(carrier)

        return messages.CarrierPigeon(message_type, hint, carrier_payload)


class HandshakeMapper(MessageMapper):
    def mapBuffer(self, buffer):
        handshake = session_handshake.GetRootAs(buffer, 0)
        return messages.Handshake(
            handshake.Username().decode('utf-8'),
            handshake.Signature().decode('utf-8'),
            handshake.CreationTime()
        )


# Mapper lookup table
mappers = {
    "carrier_pigeon": CarrierMapper(),
    "handshake": HandshakeMapper()
}


def _safe_fetch_mapper(mapper_hint):
    mapper = None
    try:
        mapper = mappers[mapper_hint]
    except KeyError:
        print("Can't map type `%s` because a mapper doesn't exist" % (mapper_hint))
        raise RuntimeError  # TODO gracefully handle this by returning an error type
    return mapper


def _carrier_has_payload(carrier):
    return carrier.payload is not None


def _deserialize_carrier_payload(carrier):
    mapper = _safe_fetch_mapper(carrier.hint)
    carrier.payload = mapper.mapBuffer(carrier.payload)


def deserialize_carrier(carrier_bytes):
    mapper = _safe_fetch_mapper("carrier_pigeon")
    carrier = mapper.mapBuffer(carrier_bytes)

    if _carrier_has_payload(carrier):
        _deserialize_carrier_payload(carrier)

    return carrier


# # # #  # # #  # # #  # # #  # # 
#           UTILITY
# # #  # # #  # # #  # # #  # # # 

def create_carrier_pigeon(message_hint, payload, type=message_types["Message"]):

    # Delegate object packing from somewhere?
    builder = flatbuffers.Builder(2048)

    # Serialize non-scalars
    # Message Hint
    hint_scalar = builder.CreateString(message_hint)

    # Serialize scalars
    carrier_pigeon.Start(builder)

    carrier_pigeon.AddHint(builder, hint_scalar)
    carrier_pigeon.AddType(builder, type)

    bufferID = carrier_pigeon.End(builder)

    # done
    builder.Finish(bufferID)
    return bytes(builder.Output())
