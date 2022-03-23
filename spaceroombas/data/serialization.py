from .state import MapSector
from . import messages
from .messages import CarrierPigeon, Handshake

from json import JSONEncoder, dumps as json_string, loads as load_json

class PayloadMapper():
    def map(self, dict):
        raise NotImplementedError

class HandshakePayloadMapper(PayloadMapper):

    def map(self, dict):
        return Handshake(dict['user'], dict['signature'], dict['time'])

carrier_mappers = {
    'handshake':HandshakePayloadMapper()
}

class CarrierPigeonEncoder(JSONEncoder):
    def default(self, obj):
        return {
            "type":obj.type,
            "payload_type":obj.payload_type,
            "payload":obj.payload
        }

class HandshakeEncoder(JSONEncoder):
    def default(self, obj):
        raise NotImplementedError
    
    def encode(self, o) -> str:
        return super().encode(o)

class MapSectorEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MapSector):
            return {
                "land_map":obj.land_map,
                "sect_up":self._safe_get_sector_id(obj.sect_up),
                "sect_down":self._safe_get_sector_id(obj.sect_down),
                "sect_left":self._safe_get_sector_id(obj.sect_left),
                "sect_right":self._safe_get_sector_id(obj.sect_right),
            }

    def _safe_get_sector_id(self, sector):
        if sector is None:
            return None
        return sector.sector_id

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
            return encoder(*self.args, **self.kwargs).default(mObj)
        except KeyError:
            return self.fallbackEncoder.default(mObj)

obj_encoders = {
            CarrierPigeon:CarrierPigeonEncoder,
            messages.Handshake:HandshakeEncoder,
            MapSector:MapSectorEncoder
}

encodingDelegator = JsonEncodingDelegator(obj_encoders)

def map_carrier(carrier_dict):
    payload_type = carrier_dict['payload_type']

    try:
        mapper = carrier_mappers[payload_type]
        try:
            carrier_payload = mapper.map(carrier_dict['payload'])
        except KeyError:
            print("Carrier payload has missing key")
            carrier_payload = None
            payload_type = "invalid"
    except KeyError:
        print("Mapper doesn't exist for payload type")
        carrier_payload = None
        payload_type = "invalid"

    return CarrierPigeon(carrier_dict['type'], payload_type, carrier_payload)

def serialize(message_type, mObj):
    objTypeName = str(type(mObj).__name__)
    pigeon = CarrierPigeon("message", objTypeName, mObj)
    return json_string(pigeon, cls=encodingDelegator, separators=(',', ':'))

package_for_shipping = lambda mObj: serialize("message", mObj)

def unpackage_carrier(carrier):
    carrier_dict = load_json(carrier)
    mapped_carrier = map_carrier(carrier_dict)
    return mapped_carrier
