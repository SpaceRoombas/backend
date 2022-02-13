from mimetypes import init


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
