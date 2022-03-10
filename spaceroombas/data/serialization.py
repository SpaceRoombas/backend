from multiprocessing.sharedctypes import Value

from .types import GameMap
from . import state
from .flats.message_type import message_type
from .flats.session_handshake import session_handshake
from .flats import game_map
from .flats import carrier_pigeon
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

class GameMapMapper(MessageMapper):

    def flatten_game_map(self, map_vector):
        vert_len = len(map_vector)
        horiz_len = len(map_vector[0])
        flattened_map = [None] * (vert_len * horiz_len)
        cell = 0
        for i in range(0, vert_len):
            for k in range(0, horiz_len):
                flattened_map[cell] = map_vector[i][k]
                cell = cell + 1
        
        return flattened_map

    def mapMessage(self, message):
        # Safety first, kids
        if type(message) is not GameMap:
            print("Cannot map unexpected type ¯\_(ツ)_/¯")

        flatmap = self.flatten_game_map(message.land_map)
        builder = flatbuffers.Builder(1024)
        game_map.StartLandMapVector(builder, len(flatmap))
        land_map_offset = util_create_vector_buffer(builder, flatmap)

        # Serialize
        game_map.Start(builder)
        game_map.AddLandMap(builder, land_map_offset)
        buffer_offset = game_map.End(builder)

        builder.Finish(buffer_offset)
        return builder.Output()

class MapSectorMapper(MessageMapper):

    def flatten_game_map(self, map_vector):
        vert_len = len(map_vector)
        horiz_len = len(map_vector[0])
        flattened_map = [None] * (vert_len * horiz_len)
        cell = 0
        for i in range(0, vert_len):
            for k in range(0, horiz_len):
                flattened_map[cell] = map_vector[i][k]
                cell = cell + 1
        
        return flattened_map

    def mapMessage(self, message):
        # Safety first, kids
        if type(message) is not state.MapSector:
            print("Cannot map unexpected type ¯\_(ツ)_/¯")

        flatmap = self.flatten_game_map(message.land_map)
        builder = flatbuffers.Builder(1024)
        game_map.StartLandMapVector(builder, len(flatmap))
        land_map_offset = util_create_vector_buffer(builder, flatmap)

        # Serialize
        game_map.Start(builder)
        game_map.AddLandMap(builder, land_map_offset)
        buffer_offset = game_map.End(builder)

        builder.Finish(buffer_offset)
        return builder.Output()

# Mapper lookup tables
mapperTypes = {
    "carrier_pigeon": CarrierMapper,
    "handshake": HandshakeMapper,
    "game_map": GameMapMapper,
    "map_sector" : MapSectorMapper,
}

mappers = {
    CarrierMapper:CarrierMapper(),
    HandshakeMapper:HandshakeMapper(),
    GameMap:GameMapMapper(),
    state.MapSector:MapSectorMapper()
}

def _safe_fetch_mapper(mapper_hint):
    mapperType = None
    mapper = None
    try:
        mapperType = mapperTypes[mapper_hint]
        mapper = mappers[mapperType]
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


def magically_package_object(mObj):
    obj_type = type(mObj)

    # Grab the mapper
    try:
        mapper = mappers[obj_type]
    except KeyError:
        print("Cannot map that type")
        return
    
    return mapper.mapMessage(mObj)



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

def util_create_vector_buffer(builder, vector):
    vecSz = len(vector)

    for i in reversed(range(0, vecSz)):
        builder.PrependByte(vector[i])
    
    return builder.EndVector()