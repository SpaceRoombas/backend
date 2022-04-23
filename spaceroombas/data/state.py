from queue import Queue

from map import mapgeneration
from roombalang import interpreter
from roombalang import parser
from roombalang import transpiler
from .util import create_interpreter_function_bindings
import logging
import random


class PlayerExistsError(RuntimeError):
    pass


# Various state change events

class RobotMoveEvent:

    def __init__(self, player_id, robot_id, old_location, new_location) -> None:
        self.player_id = player_id
        self.robot_id = robot_id
        self.old = old_location
        self.new = new_location


class MapSector:
    def __init__(self, sector_id) -> None:
        # TODO update map to hold more information...
        self.land_map = mapgeneration.generate()
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


class EntityLocation:

    def __init__(self, sector, x, y) -> None:
        # TODO This references the whole sector object, when really it should be a sector id
        # Consider setting this as sector ID. The rest of the logic that uses this location class
        # Assumes this will return a MapSector.
        # When updating this, make sure to adjust EntityLocationEncoder in serialization.py
        self.sector = sector
        self.x = x
        self.y = y

    def __str__(self):
        return "sec:" + self.sector.sector_id + " x,y:" + str(self.x) + "," + str(self.y)

    def get_sector_id(self):
        return self.sector.sector_id


class MapState:

    def __init__(self):
        # Generate first map sector
        self.__sectors = dict()
        # self.generate_map_sector("0,0")

    def resolve_location(self, location: EntityLocation):
        x = location.x
        y = location.y

        xMax = 49
        yMax = 49

        starting_sector_id = location.sector.sector_id
        sec_x, sec_y = MapSector.parse_id(starting_sector_id)

        if x < 0:  # move left
            sec_x -= 1
            x = xMax
        elif y < 0:  # move up
            sec_y += 1
            y = yMax
        elif x > xMax:  # move right
            sec_x += 1
            x = 0
        elif y > yMax:  # move down
            sec_y -= 1
            y = 0
        else:
            return location, False

        new_sector_id = MapSector.form_sector_id(sec_x, sec_y)
        return EntityLocation(self.get_sector(new_sector_id), x, y), True

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
                return False
        else:
            return False

    def get_sector_ids(self):
        return list(self.__sectors.keys())

    def get_sector(self, sector_id):
        if self.__sectors.get(sector_id) is None:
            logging.warning("couldnt find sector: %s" % (sector_id))
            return None
        else:
            return self.__sectors[sector_id]

    def sector_count(self):
        logging.info(len(self.__sectors.keys()))
        return len(self.__sectors.keys())

    def generate_map_sector(self, center_sector_id):
        def make_sector(sector_id):
            if self.__sectors.get(sector_id) is None:
                self.__sectors[sector_id] = MapSector(sector_id)
                x, y = MapSector.parse_id(sector_id)
                self.connect_sectors(
                    sector_id, MapSector.form_sector_id(x + 1, y))
                self.connect_sectors(
                    sector_id, MapSector.form_sector_id(x - 1, y))
                self.connect_sectors(
                    sector_id, MapSector.form_sector_id(x, y + 1))
                self.connect_sectors(
                    sector_id, MapSector.form_sector_id(x, y - 1))
                logging.debug("Make new sector: %s" % (sector_id))
                return True
            else:
                logging.warning("Sector already exists: %s" % (sector_id))
                return False

        x, y = MapSector.parse_id(center_sector_id)
        sec_delta = [(-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0),
                     (1, 0), (-1, -1), (0, -1), (1, -1)]
        for sec_d in sec_delta:
            make_sector(MapSector.form_sector_id(x+sec_d[0], y+sec_d[1]))

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

    def check_tile_mineable(self, location: EntityLocation):
        if self.violates_map_bounds(location.x, location.y):
            return False

        current_sector = self.get_sector(location.sector.sector_id)
        return current_sector.land_map[location.x][location.y][1] == 1

    def mine_tile(self, location: EntityLocation):
        if self.check_tile_mineable(location):
            current_sector = self.get_sector(location.sector.sector_id)
            current_sector.land_map[location.x][location.y][1] = 0
            current_sector.land_map[location.x][location.y][1] = True
            return True
        return False


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
        self.bound_functions = {}
        self.resources = 0

        self.init_default_robot()

    def tick(self):
        if self.interpreter is not None:
            self.interpreter.tick()

    def init_default_robot(self):
        self.set_firmware(
            "while(true){move(rand_dir()) reproduce(rand_dir()) mine(rand_dir()) terraform()}")

    def init_interpreter(self):
        self.interpreter = interpreter.Interpreter(
            self.firmware, self.bound_functions, self.parser, self.transpiler)

    def set_firmware(self, code):
        self.firmware = code
        try:
            self.init_interpreter()
        except:
            logging.info(
                f"Robot {self.owner}:{self.robot_id} had syntax error")

    def set_bound_functions(self, fns: dict):
        if type(fns) != dict:
            self.bound_functions = {}
            return

        self.bound_functions = fns
        if self.interpreter is not None:
            self.interpreter.set_fns(self.bound_functions)

    def terraform(self, state):
        if self.resources >= 4:
            self.resources -= 4
            state.players[self.owner].score += 1

    def mine(self, state, direction):
        """mines a resource in the direction specified, 0=N 1=E 2=S 3=W"""

        mine_pos = EntityLocation(
            self.location.sector, self.location.x, self.location.y)

        if direction == 0:
            mine_pos.y += 1
        elif direction == 1:
            mine_pos.x += 1
        elif direction == 2:
            mine_pos.y -= 1
        else:
            mine_pos.x -= 1

        if state.map.mine_tile(mine_pos):
            self.resources += 1

    def look(self, state, direction):
        """returns id of tile type, -2 if map edge, or -1 if robot"""

        look_pos = EntityLocation(
            self.location.sector, self.location.x, self.location.y)

        if direction == 0:
            look_pos.y += 1
        elif direction == 1:
            look_pos.x += 1
        elif direction == 2:
            look_pos.y -= 1
        else:
            look_pos.x -= 1

        if state.map.violates_map_bounds(look_pos.x, look_pos.y):
            return -2

        sector = state.map.get_sector(direction.sector.sector_id)

        if not state.map.check_tile_available(look_pos) and sector.land_map[look_pos.x][look_pos.y][1] == 0:
            return -1

        else:
            return sector.land_map[look_pos.x][look_pos.y][1]

    def reproduce(self, state, direction):
        """creates a new robot in the direction specified, 0=N 1=E 2=S 3=W"""

        new_pos = EntityLocation(self.location.sector,
                                 self.location.x, self.location.y)

        if direction == 0:
            new_pos.y += 1
        elif direction == 1:
            new_pos.x += 1
        elif direction == 2:
            new_pos.y -= 1
        else:
            new_pos.x -= 1

        if state.map.check_tile_available(new_pos) and self.resources >= 1:
            self.resources -= 1
            state.add_robot(self.owner, new_pos)


class PlayerState:
    def __init__(self, player_id, sector_id, parser, transpiler):
        self.home_sector = sector_id
        self.player_id = player_id
        self.robots = dict()
        self.player_firmware = None
        self.parser = parser
        self.transpiler = transpiler
        self.change_events = Queue()
        self.score = 0

    def add_robot(self, location: EntityLocation):
        robot = PlayerRobot(self.player_id, location,
                            self.parser, self.transpiler)
        self.robots[robot.robot_id] = robot
        return robot

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
        self.NEW_ROBOT_FLAG = False

    def add_player(self, player_id):
        x, y = self.choose_spawn_sector()
        sector_id = MapSector.form_sector_id(x, y)

        self.map.generate_map_sector(sector_id)
        sector = self.map.get_sector(sector_id)

        playerState = PlayerState(
            player_id, sector, self.parser, self.transpiler)

        if player_id in self.players:  # TODO implement logic here for orphan clients
            raise PlayerExistsError("Player already exists")

        self.players[player_id] = playerState

        x = 20
        y = 20
        while False == self.map.check_tile_available(EntityLocation(sector, x, y)):
            logging.warning("tile in use", x, y, sector_id)
            x += 1

        self.add_robot(player_id, EntityLocation(sector, x, y))
        logging.info("Player added: %s" % (player_id))

    def choose_spawn_sector(self):
        # returns false if any point is with in the distance
        def check_distance(x1, y1, previous, dist):
            for p in previous:
                if dist > abs(x1-p[0])+abs(y1-p[1]):  # manhattan distance
                    return False
            return True

        indexs = []
        sectors = self.map.get_sector_ids()

        for s in sectors:
            indexs.append(MapSector.parse_id(s))

        xdelta = 0
        ydelta = 0
        x = 0
        y = 0
        distance = random.randint(3, 6)
        while xdelta == 0 and ydelta == 0:
            xdelta = random.randint(-1, 1)
            ydelta = random.randint(-1, 1)

        while check_distance(x, y, indexs, distance) == False:
            x += xdelta
            y += ydelta
        return x, y

    # TODO set up so the robot is spawned in valid location
    def add_robot(self, player_id, location: EntityLocation):
        robot = None
        if self.players.get(player_id) is None:
            logging.warning("invalid player id to add robot to")
            return False
        else:
            robot = self.players[player_id].add_robot(location)
            self.__bind_robot_functions(robot)
            self.map.update_walkable(location, False)
            self.NEW_ROBOT_FLAG = True
            return True

    def __bind_robot_functions(self, robot: PlayerRobot):
        fns = create_interpreter_function_bindings(self, robot)
        robot.set_bound_functions(fns)

    def get_robot(self, player_id, robot_id):
        try:
            player = self.players[player_id]
            return player.robots[robot_id]
        except KeyError:
            logging.warn("Tried to fetch robot %s:%s, but doesn't exist" %
                         (player_id, robot_id))
            return

    def get_player_robots(self, player_id):
        try:
            player = self.players[player_id]
        except KeyError:
            logging.warning("Player '%s' doesnt exist" % (player_id))
            return None
        return player.robots

    def check_for_new_robots(self):
        if self.NEW_ROBOT_FLAG == True:
            self.NEW_ROBOT_FLAG = False
            return self.get_all_robots()

    def get_all_robots(self):
        bots = [None] * PlayerRobot.robot_count
        i = 0
        for player in self.players.values():
            for robot in player.robots.values():
                bots[i] = robot
                i += 1
        return bots

    def move_player_robot(self, player_id, robot_id, dx=0, dy=0):
        robot: PlayerRobot = None
        player: PlayerState = None
        try:
            player = self.players[player_id]
            robot = player.robots[robot_id]
        except KeyError:
            logging.info("Failed to fetch player or robot %s:%s" %
                         (player_id, robot_id))
            return

        # Check co-ord params and set current location (no change in that co-ord)
        if dx == 0 and dy == 0:
            logging.warn(
                "Robot move got bad location delta: X: %s Y: %s" % (dx, dy))
            return False

        wantedLocation = EntityLocation(
            robot.location.sector, robot.location.x + dx, robot.location.y + dy)
        wantedLocation, changed = self.map.resolve_location(wantedLocation)

        if changed:  # if new sector... make new sector on map
            self.map.generate_map_sector(wantedLocation.sector.sector_id)

        if self.map.check_tile_available(wantedLocation):
            # Add event
            player.add_state_change_event(RobotMoveEvent(
                player_id, robot_id, robot.location, wantedLocation))

            # Adjust state
            self.map.update_walkable(robot.location, True)
            robot.location = wantedLocation
            self.map.update_walkable(wantedLocation, False)
            return True
        else:
            logging.debug("\"%s:%s\" wanted tile in use: %s" %
                          (player_id, robot_id, wantedLocation))
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
