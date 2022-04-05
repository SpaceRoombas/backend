from queue import Queue
from site import setcopyright
from tokenize import String
from map import mapgeneration
from uuid import uuid4
from roombalang import interpreter
from roombalang import parser
from roombalang import transpiler


class PlayerExistsError(RuntimeError):
    pass

# Various state change events

class RobotMoveEvent():

    def __init__(self, player_id, robot_id, old_location, new_location) -> None:
        self.player_id = player_id
        self.robot_id = robot_id
        self.old = old_location
        self.new = new_location


class MapSector():
    def __init__(self, sector_id) -> None:
        self.land_map = mapgeneration.generate()  # TODO update map to hold more information... like walkable
        self.sector_id = sector_id
        self.sect_up = None
        self.sect_down = None
        self.sect_left = None
        self.sect_right = None

    def parse_id(sector_id):
        x, y = sector_id.split(",")
        return int(x), int(y)

    def form_sector_id(x, y):
        return str(x) + "," + str(y)


class EntityLocation():
    """
    sector is the id of the sector that the entity is located
    """

    def __init__(self, sector, x, y) -> None:
        self.sector = sector
        self.x = x
        self.y = y

    def __str__(self):
        return "sec:" + self.sector.sector_id + " x,y:" + str(self.x) + "," + str(self.y)


class MapState():

    def __init__(self):
        # Generate first map sector
        self.__sectors = dict()
        self.generate_map_sector("0,0")

    def connect_sectors(self, sector1id, sector2id):
        if self.__sectors.get(sector1id) is not None and self.__sectors.get(sector2id) is not None:
            sector1 = self.__sectors.get(sector1id)
            sector2 = self.__sectors.get(sector2id)
            x1, y1 = MapSector.parse_id(sector1id)
            x2, y2 = MapSector.parse_id(sector2id)

            if x1 - 1 == x2 and y1 == y2:  # if sec2 is to the left
                sector1.sect_left = sector2
                sector2.sect_right = sector1
                return True
            elif x1 + 1 == x2 and y1 == y2:  # if sec2 is to the right
                sector1.sect_right = sector2
                sector2.sect_left = sector1
                return True
            elif x1 == x2 and y1 + 1 == y2:  # if sec2 is up
                sector1.sect_up = sector2
                sector2.sect_down = sector1
                return True
            elif x1 == x2 and y1 - 1 == y2:  # if sec2 is down
                sector1.sect_down = sector2
                sector2.sect_up = sector1
                return True
            else:
                # print("sectors do not connect",sector1id,sector2id)
                return False
        else:
            # print("sectors do not exist in map",sector1id,sector2id)
            return False

    def get_sector(self, sector_id):
        if self.__sectors.get(sector_id) is None:
            print("couldnt find sector")
            return None
        else:
            return self.__sectors[sector_id]

    def sector_count(self):
        print(len(self.__sectors.keys()))
        return len(self.__sectors.keys())

    def generate_map_sector(self, sector_id):  ## TODO incorporate logic for adding to current graph/ update ID
        if self.__sectors.get(sector_id) is None:
            self.__sectors[sector_id] = MapSector(sector_id)
            x, y = MapSector.parse_id(sector_id)
            self.connect_sectors(sector_id, MapSector.form_sector_id(x + 1, y))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x - 1, y))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x, y + 1))
            self.connect_sectors(sector_id, MapSector.form_sector_id(x, y - 1))
            return True

        else:
            print("error sector already created")
            return False

    def update_walkable(self, location: EntityLocation, walkable):
        current_sector = self.get_sector(location.sector.sector_id)
        current_sector.land_map[location.x][location.y][0] = walkable

    def violates_map_bounds(self, x, y):
        # TODO this is hard coded, we need to update this to reflect actual map bounds
        xMax = 49
        yMax = 49

        return x > xMax or y > yMax or y < 0 or x < 0

    def check_tile_available(self, location: EntityLocation):

        if self.violates_map_bounds(location.x, location.y):
            return False

        current_sector = self.get_sector(location.sector.sector_id)
        return current_sector.land_map[location.x][location.y][0]


class GameObject:  # TODO game object... we can have buildings ext
    def __init__(self, owner_id, location: EntityLocation):
        self.owner = owner_id
        self.location = location
        self.firmware = None  # TODO add current firmware/ function being run by robot


class PlayerRobot:  # TODO make player robot inherit from a general game object
    robot_count = 0

    def __init__(self, owner_id, location: EntityLocation, parser, transpiler):
        self.owner = owner_id
        self.robot_id = "r" + str(self.robot_count)
        PlayerRobot.robot_count += 1
        self.location = location
        self.firmware = None
        self.parser = parser
        self.transpiler = transpiler
        self.interpreter = None

        self.init_default_robot()

    def tick(self, fns):
        self.interpreter.set_fns(fns)
        self.interpreter.tick()

    def init_default_robot(self):
        self.set_firmware("while(true){move_north() move_east() move_south() move_west()}")

    def init_interpreter(self):
        self.interpreter = interpreter.Interpreter(self.firmware, {}, self.parser, self.transpiler)

    def set_firmware(self, code):
        self.firmware = code
        self.init_interpreter()

class PlayerState:
    def __init__(self, player_id, sector_id, parser, transpiler):
        self.home_sector = sector_id
        self.player_id = player_id
        self.robots = dict()
        self.player_firmware = None
        self.parser = parser
        self.transpiler = transpiler
        self.change_events = Queue()

    def add_robot(self, location: EntityLocation):
        robot = PlayerRobot(self.player_id, location, self.parser, self.transpiler)
        self.robots[robot.robot_id] = robot
    
    def add_state_change_event(self, change_event):
        self.change_events.put(change_event)
    
    def get_list_state_change_events(self):
        events = list()

        while not self.change_events.empty():
            events.append(self.change_events.get())
        
        return events

class GameState:
    def __init__(self):
        self.map = MapState()
        self.players = dict()
        self.parser = parser.Parser()
        self.transpiler = transpiler.Transpiler()

    def add_player(self, player_id):
        sector = self.map.get_sector(
            "0,0")  # TODO implement logic to spawn new player in their own starting sector/for now to base
        playerState = PlayerState(player_id, sector, self.parser, self.transpiler)

        if player_id in self.players:  ## TODO implement logic here for orphan clients
            raise PlayerExistsError("Player already exists")

        self.players[player_id] = playerState
        x = 20  # TODO implement logic to spawn starting robot not in a used tile
        y = 20
        self.add_robot(player_id, EntityLocation(sector, x, y))

    def add_robot(self, player_id, location: EntityLocation):  # TODO set up so the robot is spawned in valid location
        if self.players.get(player_id) is None:
            print("invalid player id to add robot to")
            return False
        else:
            self.players[player_id].add_robot(location)
            self.map.update_walkable(location, False)
            return True

    def get_robot(self, player_id, robot_id):
        player = self.players[player_id]
        return player.robots[robot_id]

    def get_player_robots(self, player_id):
        try:
            player = self.players[player_id]
        except KeyError:
            print("Player '%s' doesnt exist" % (player_id))
            return None
        return player.robots

    def move_player_robot(self, player_id, robot_id, dx=0, dy=0):
        robot: PlayerRobot = None
        player: PlayerState = None
        try:
            player = self.players[player_id]
            robot = player.robots[robot_id]
        except KeyError:
            print("Failed to fetch player or robot that doesnt exist")
            return

        # Check co-ord params and set current location (no change in that co-ord)
        if dx == 0 and dy == 0:
            print("Passed bad location")
            return False

        wantedLocation = EntityLocation(robot.location.sector, robot.location.x + dx, robot.location.y + dy)

        if self.map.check_tile_available(wantedLocation):
            # Add event
            player.add_state_change_event(RobotMoveEvent(player_id, robot_id, robot.location, wantedLocation))

            # Adjust state
            self.map.update_walkable(robot.location, True)
            robot.location = wantedLocation
            self.map.update_walkable(wantedLocation, False)
            return True
        else:
            print("tile was in use: %s" % (wantedLocation))
            return False

    # Aliases for robot movement
    def move_robot_up(self, player_id, robot_id):
        return self.move_player_robot(player_id, robot_id, 0, -1)

    def move_robot_down(self, player_id, robot_id):
        return self.move_player_robot(player_id, robot_id, 0, 1)

    def move_robot_left(self, player_id, robot_id):
        return self.move_player_robot(player_id, robot_id, -1, 0)

    def move_robot_right(self, player_id, robot_id):
        return self.move_player_robot(player_id, robot_id, 1, 0)

# TODO add logic for movement between sectors, check movement code to be neater

