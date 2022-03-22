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
    def parse_id(sector_id):
        x,y = sector_id.split(",")
        return int(x),int(y)

    def form_sector_id(x,y):
        return str(x)+","+str(y)

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
    
    def connect_sectors(self,sector1id,sector2id):
        if self.__sectors.get(sector1id) != None and self.__sectors.get(sector2id) != None:
            sector1 = self.__sectors.get(sector1id)
            sector2 = self.__sectors.get(sector2id)
            x1,y1= MapSector.parse_id(sector1id)
            x2,y2= MapSector.parse_id(sector2id)

            if(x1-1==x2 and y1==y2): #if sec2 is to the left
                sector1.sect_left = sector2
                sector2.sect_right = sector1
                return True
            elif(x1+1==x2 and y1==y2): #if sec2 is to the right
                sector1.sect_right = sector2
                sector2.sect_left = sector1
                return True
            elif(x1==x2 and y1+1==y2): #if sec2 is up
                sector1.sect_up = sector2
                sector2.sect_down = sector1
                return True
            elif(x1==x2 and y1-1==y2): #if sec2 is down
                sector1.sect_down = sector2
                sector2.sect_up = sector1
                return True
            else:
                print("sectors do not connect",sector1id,sector2id)
                return False
        else:
            print("sectors do not exist in map",sector1id,sector2id)
            return False

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
            x,y= MapSector.parse_id(sector_id)
            self.connect_sectors(sector_id, MapSector.form_sector_id(x+1,y))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x-1,y))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x,y+1))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x,y-1))
            return True

        else:
            print("error sector already created")
            return False
    def update_walkable(self,location: EntityLocation, walkable):
        current_sector = self.get_sector(location.sector.sector_id)
        current_sector.land_map[location.x][location.y][0] = walkable

    def check_tile_used(self,location: EntityLocation):   
        current_sector = self.get_sector(location.sector.sector_id)
        return current_sector.land_map[location.x][location.y][0]


class GameObject(): #TODO game object... we can have buildings ext
    def __init__(self, owner_id, location: EntityLocation):
        self.owner = owner_id
        self.location = location
        self.firmware = None #TODO add current firmware/ function being run by robot

class PlayerRobot():#TODO make player robot inherit from a general game object 
    robot_count = 0
    def __init__(self, owner_id, location: EntityLocation):
        self.owner = owner_id
        self.robot_id = "r"+str(self.robot_count)
        self.robot_count += 1
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
        if self.players.get(player_id) == None:
            print("invalid player id to add robot too")
            return False
        else:
            self.players[player_id].add_robot(location)
            self.map.update_walkable(location,False)
            return True


    def move_robot_left(self,player_id,robot_id):
        return

# TODO logic for orphan client
