from argparse import ArgumentError
from site import setcopyright
from tokenize import String
from map import mapgeneration
from uuid import uuid4

class PlayerExistsError(ArgumentError):
    pass



class MapSector():   
    def __init__(self, sector_id) -> None:
        self.land_map = mapgeneration.generate()# TODO update map to hold more information... like walkable
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

class MapState():

    def __init__(self):
        # Generate first map sector
        self.__sectors = dict()
        self.generate_map_sector("0,0")
    
    def parse_id(sector_id):
        x,y = sector_id.split(",")
        return int(x),int(y)

    def form_sector_id(x,y):
        return str(x)+","+str(y)

    def get_sector(self, sector_id):
        if self.__sectors.get(sector_id) == None:
            print("couldnt find sector")
            return None
        else:
            return self.__sectors[sector_id]

    def sector_count(self):
        print(len(self.__sectors.keys()))
        return len(self.__sectors.keys())

    def generate_map_sector(self,sector_id): ## TODO incorporate logic for adding to current graph/ update ID
        if self.__sectors.get(sector_id) == None:
            self.__sectors[sector_id] = MapSector(sector_id)
        else:
            print("error sector already created")##TODO idk if this should be a true error or just something that happens

    def update_walkable(self,location: EntityLocation, walkable):
        current_sector = self.get_sector(location.sector.sector_id)
        current_sector.land_map[location.x][location.y][0] = walkable

    def check_tile_used(self,location: EntityLocation):
        
        current_sector = self.get_sector(location.sector.sector_id)
        return current_sector.land_map[location.x][location.y][0]


    
class PlayerRobot(): 
    def __init__(self, owner_id, location: EntityLocation):
        self.owner = owner_id
        self.location = location
        self.firmware = None #TODO add current firmware/ function being run by robot

class PlayerState():

    def __init__(self, player_id,sector_id):
        self.home_sector = sector_id
        self.player_id = player_id
        self.robots = list() 
        self.player_firmware = None
    
    def add_robot(self,location: EntityLocation):
        self.robots.append(PlayerRobot(self.player_id,location))
        

class GameState():
    def __init__(self):
        self.map = MapState()
        self.players = dict()

    def add_player(self, player_id):
        sector = self.map.get_sector("0,0") #TODO implement logic to spawn new player in their own starting sector/for now to base
        playerState = PlayerState(player_id,sector)

        if player_id in self.players:## TODO implement logic here for orphan
            raise PlayerExistsError("Player already exists")
        self.players[player_id] = playerState
        x=20#TODO implement logic to spawn starting robot not in a used tile
        y=20
        self.add_robot(player_id,EntityLocation(sector,x,y))

    def add_robot(self,player_id,location: EntityLocation):
        print(self.map.check_tile_used(location))
        if self.players.get(player_id) == None:
            print("invalid player id to add robot too")
        else:
            self.players[player_id].add_robot(location)
            self.map.update_walkable(location,False)
        print(self.map.check_tile_used(location))
# TODO write code to do robot movement.... include moving in map and sector.

# TODO logic for orphan client
