class CarrierPigeon:
    def __init__(self, type=None, payload_type=None, payload=None):
        self.type = type
        self.payload_type = payload_type
        self.payload = payload


class Handshake:
    STATUS_OK = 200
    STATUS_ORPHAN_OK = 201
    STATUS_VERIFY_FAILED = 403

    def __init__(self, username=None, signature=None, status=None):
        self.username = username
        self.signature = signature
        self.status = status


class PlayerDetails:
    def __init__(self, name, server, token_time, match_expire, signature):
        self.username = name
        self.server = server
        self.token_time = token_time
        self.match_expire = match_expire
        self.signature = signature


class PlayerFirmwareChange:

    def __init__(self, code, player_id, robot_id=None):
        self.code = code
        self.player_id = player_id
        self.robot_id = robot_id
        pass


class MapUpdateRequestMessage:

    def __init__(self, chunk="all") -> None:
        self.req_chunk = chunk
        self.data = None


class NewConnectionMessage:
    def __init__(self, client_id) -> None:
        self.client_id = client_id


class PlayerRobotMoveMessage:

    def __init__(self, player_id, robot_id, x, y):
        self.player_id = player_id
        self.robot_id = robot_id
        self.x = x
        self.y = y


class PlayerRobotErrorMessage:

    def __init__(self, player_id, robot_id, error):
        self.player_id = player_id
        self.robot_id = robot_id
        self.error = error


class RobotListingMessage:

    def __init__(self, bots=[]) -> None:
        self.num_bots = len(bots)
        self.robots = bots
