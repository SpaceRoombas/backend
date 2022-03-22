from argparse import ArgumentError
from tokenize import String
from map import mapgeneration
from uuid import uuid4

class PlayerExistsError(ArgumentError):
    pass

class MapSector():
    
    def __init__(self, sector_id) -> None:
        self.land_map = mapgeneration.generate()
        self.sector_id = sector_id
        self.sect_up = None
        self.sect_down = None
        self.sect_left = None
        self.sect_right = None

class EntityLocation():
    """
    sector is the id of the sector that the entity is located
    """
    def __init__(self, sector, x, y) -> None:
        self.sector = sector
        self.x = x
        self.y = y
    
class PlayerRobot():
    def __init__(self, owner_id, location: EntityLocation):
        self.owner = owner_id
        self.location = location

class PlayerState():

    def __init__(self, player_id):
        self.player_id = player_id
        self.robots = list() # TODO probably add default robot?
        self.player_firmware = None
        
        # Player starts with 1 robot
        # TODO assign robot to player

class GameState():
    def __init__(self):
        self.map = MapState()
        self.players = dict()

    def add_player(self, player_id) -> None:

        playerState = PlayerState(player_id)

        if player_id in self.players:
            raise PlayerExistsError("Player already exists")
        self.players[player_id] = playerState

class MapState():

    def __init__(self):
        # Generate first map sector
        self.__sectors = list()
        self.generate_map_sector()
    
    def get_sector(self, sector_id):
        try:
            return self.__sectors[sector_id]
        except IndexError:
            return None

    def sector_count(self):
        return len(self.__sectors)
    
    def next_sector_id(self):
        return self.sector_count() + 1

    def generate_map_sector(self):
        sector = MapSector(self.next_sector_id())
        self.__sectors.append(sector)
    
