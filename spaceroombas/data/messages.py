class CarrierPigeon():
    def __init__(self, type=None, hint=None, payload=None):
        self.type = type
        self.hint = hint
        self.payload = payload


class Handshake():
    def __init__(self, username=None, signature=None, creation_time=None):
        self.creation_time = creation_time
        self.username = username
        self.signature = signature

class MapUpdateRequestMessage():

    def __init__(self, chunk="all") -> None:
        self.req_chunk = chunk
        self.data = None

class NewConnectionMessage():
    def __init__(self, client_id) -> None:
        self.client_id = client_id