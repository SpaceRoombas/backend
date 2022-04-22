from .state import MapSector, PlayerRobot, EntityLocation
from . import messages
from .messages import CarrierPigeon, Handshake, PlayerDetails, PlayerFirmwareChange, PlayerRobotMoveMessage

from json import JSONEncoder, dumps as json_string, loads as load_json
import logging
# ---------------------------
#
# Payload Mappers
#
# ---------------------------


class PayloadMapper():
    def map(self, dict):
        raise NotImplementedError


class HandshakePayloadMapper(PayloadMapper):

    def map(self, dict):
        return Handshake(dict['username'], dict['signature'], dict['status'])


class PlayerDetailsMapper(PayloadMapper):
    def map(self, dict):
        return PlayerDetails(dict['player_name'], dict['server_address'],
                             dict['token_millis'], dict['match_end_millis'], dict['signature'])


class PlayerFirmwareChangeMapper(PayloadMapper):

    def map(self, dict):
        return PlayerFirmwareChange(dict['code'], dict['player_id'], dict['robot_id'])


# ---------------------------
#
# JSON Encoders
#
# ---------------------------


class CarrierPigeonEncoder(JSONEncoder):
    def default(self, obj):
        return {
            "type": obj.type,
            "payload_type": obj.payload_type,
            "payload": obj.payload
        }


class HandshakeEncoder(JSONEncoder):
    def default(self, obj):
        return {
            'username': obj.username,
            'status': obj.status,
            'signature': obj.signature
        }

    def encode(self, o) -> str:
        return super().encode(o)


class PlayerFirmwareChangeEncoder(JSONEncoder):
    def default(self, obj):
        return {
            "code": obj.code,
            "player_id": obj.player_id,
            "robot_id": obj.robot_id
        }


class MapSectorEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MapSector):
            # Package land map
            # Note: This is probably expensive
            mapsz = self._get_map_size(obj.land_map)
            return {
                "sector_id": obj.sector_id,
                "land_map": self.encode_landmap(obj.land_map),
                "map_rows": mapsz[0],
                "map_cols": mapsz[1],
                "sect_up": self._safe_get_sector_id(obj.sect_up),
                "sect_down": self._safe_get_sector_id(obj.sect_down),
                "sect_left": self._safe_get_sector_id(obj.sect_left),
                "sect_right": self._safe_get_sector_id(obj.sect_right),
            }

    def _safe_get_sector_id(self, sector):
        if sector is None:
            return None
        return sector.sector_id

    def _get_map_size(self, map):
        return (len(map), len(map[0]))  # We will assume square maps

    def encode_landmap(self, map):
        mapsz = self._get_map_size(map)
        totalLen = (mapsz[0] * mapsz[1])
        pos = 0

        # Calculate
        encoded = [None] * totalLen
        for row in map:
            for tile in row:
                encoded[pos] = str(tile[1])
                pos = pos + 1
        return "".join(encoded)


class RobotMoveMessageEncoder(JSONEncoder):
    def default(self, obj):
        return {
            "player_id": obj.player_id,
            "robot_id": obj.robot_id,
            "x": obj.x,
            "y": obj.y
        }


class RobotListingEncoder(JSONEncoder):
    def default(self, obj: messages.RobotListingMessage):
        return {
            "num_robots": obj.num_bots,
            "robots": obj.robots,
        }


class EntityLocationEncoder(JSONEncoder):
    def default(self, obj: EntityLocation):
        return {
            "sector_id": obj.sector.sector_id,
            "x": obj.x,
            "y": obj.y
        }


class PlayerRobotEncoder(JSONEncoder):
    def default(self, obj: PlayerRobot):
        return {
            "owner": obj.owner,
            "robot_id": obj.robot_id,
            "location": obj.location,
            "firmware": obj.firmware,
        }


class JsonEncodingDelegator(JSONEncoder):

    def __init__(self, encoders) -> None:
        super().__init__()
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def __call__(self, *args, **kwds):
        self.args = args
        self.kwargs = kwds

        self.fallbackEncoder = JSONEncoder(*self.args, **self.kwargs)
        json_encoder = JSONEncoder(*args, **kwds)
        json_encoder.default = self.default
        return json_encoder

    def default(self, mObj):
        objType = type(mObj)
        try:
            encoder = self.encoders[objType]
            # This could be slow for high-volume messages
            return encoder(*self.args, **self.kwargs).default(mObj)
        except KeyError:
            return self.fallbackEncoder.default(mObj)

# ---------------------------
#
# Lookup Maps
#
# ---------------------------


carrier_mappers = {
    'handshake': HandshakePayloadMapper(),
    'player_details': PlayerDetailsMapper(),
    'firmware_change': PlayerFirmwareChangeMapper(),
}

obj_encoders = {
    CarrierPigeon: CarrierPigeonEncoder,
    messages.Handshake: HandshakeEncoder,
    MapSector: MapSectorEncoder,
    PlayerFirmwareChange: PlayerFirmwareChangeEncoder,
    PlayerRobotMoveMessage: RobotMoveMessageEncoder,
    messages.RobotListingMessage: RobotListingEncoder,
    PlayerRobot: PlayerRobotEncoder,
    EntityLocation: EntityLocationEncoder,
}


# ---------------------------
#
# Logic
#
# ---------------------------

encodingDelegator = JsonEncodingDelegator(obj_encoders)


def map_carrier(carrier_dict):
    payload_type = carrier_dict['payload_type']

    try:
        mapper = carrier_mappers[payload_type]
        try:
            carrier_payload = mapper.map(carrier_dict['payload'])
        except KeyError:
            logging.warn("Carrier payload has missing key")
            carrier_payload = None
            payload_type = "invalid"
    except KeyError:
        logging.warn("Mapper doesn't exist for payload type")
        carrier_payload = None
        payload_type = "invalid"

    return CarrierPigeon(carrier_dict['type'], payload_type, carrier_payload)


def serialize(message_type, mObj):
    objTypeName = str(type(mObj).__name__)
    pigeon = CarrierPigeon(message_type, objTypeName, mObj)
    return json_string(pigeon, cls=encodingDelegator, separators=(',', ':'))


def package_for_shipping(mObj): return serialize("message", mObj)


def unpackage_carrier(carrier):
    carrier_dict = load_json(carrier)
    mapped_carrier = map_carrier(carrier_dict)
    return mapped_carrier
