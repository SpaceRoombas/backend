from data import state


def test_expand_map(): #checks to see if map has walkable value and value for there being a wall/type of tile...Right now check if they are the same
    sector1 = state.MapSector("iddeeznuts")
    print(sector1.land_map)
    for row in sector1.land_map:
        for tile in row:
            assert tile[0] == True and tile[1] == 0 or tile[0] == False and tile[1] == 1

def test_sector_parsor():
    sector_id = "0,0"
    assert state.MapSector.parse_id(sector_id) == (0,0)
    sector_id = "203,192"
    assert state.MapSector.parse_id(sector_id) == (203,192)
    sector_id = "-203,192"
    assert state.MapSector.parse_id(sector_id) == (-203,192)
    sector_id = "-203,-192"
    assert state.MapSector.parse_id(sector_id) == (-203,-192)
    sector_id = "203,-192"
    assert state.MapSector.parse_id(sector_id) == (203,-192)

def test_sectorid_fromindex():
    x=0
    y=0
    assert state.MapSector.form_sector_id(x,y) =="0,0"
    x=-1
    y=-2131
    assert state.MapSector.form_sector_id(x,y) =="-1,-2131"
    x=12
    y=-2131
    assert state.MapSector.form_sector_id(x,y) =="12,-2131"

def test_duplicate_sector():
    game_state = state.GameState()
    assert game_state.map.sector_count() == 1
    assert game_state.map.generate_map_sector("0,0") == False
    assert game_state.map.sector_count() == 1
    assert game_state.map.generate_map_sector("1,0") == True
    assert game_state.map.sector_count() == 2

def test_connecting_sectors():
    game_state = state.GameState()
    sector0 = game_state.map.get_sector("0,0")

    game_state.map.generate_map_sector("0,1")
    sector1 = game_state.map.get_sector("0,1")
    assert game_state.map.connect_sectors(sector0.sector_id,sector1.sector_id) == True
    assert sector0.sect_up == sector1
    assert sector1.sect_down == sector0

    game_state.map.generate_map_sector("1,0")
    sector2 = game_state.map.get_sector("1,0")
    assert game_state.map.connect_sectors(sector0.sector_id,sector2.sector_id) == True
    assert sector0.sect_right == sector2
    assert sector2.sect_left == sector0

    game_state.map.generate_map_sector("-1,0")
    sector3 = game_state.map.get_sector("-1,0")
    assert game_state.map.connect_sectors(sector0.sector_id,sector3.sector_id) == True
    assert sector0.sect_left == sector3
    assert sector3.sect_right == sector0

    game_state.map.generate_map_sector("0,-1")
    sector4 = game_state.map.get_sector("0,-1")
    assert game_state.map.connect_sectors(sector0.sector_id,sector4.sector_id) == True
    assert sector0.sect_down == sector4
    assert sector4.sect_up == sector0

    game_state.map.generate_map_sector("0,-20")
    sector5 = game_state.map.get_sector("0,-20")
    print(sector5.sector_id)
    print(sector0.sector_id)
    assert game_state.map.connect_sectors(sector0.sector_id,sector5.sector_id) == False
    

def test_adding_new_sectors():
    game_state = state.GameState()
    game_state.map.generate_map_sector("1,0")
    game_state.map.generate_map_sector("-1,0")
    game_state.map.generate_map_sector("0,1")
    game_state.map.generate_map_sector("0,-1")
    game_state.map.generate_map_sector("1,1")
    
    sector0 = game_state.map.get_sector("0,0")
    sector1 = game_state.map.get_sector("1,0")
    assert sector0.sect_right == sector1
    assert sector1.sect_left == sector0

    sector1 = game_state.map.get_sector("-1,0")
    assert sector0.sect_left == sector1
    assert sector1.sect_right == sector0

    sector1 = game_state.map.get_sector("0,1")
    assert sector0.sect_up == sector1
    assert sector1.sect_down == sector0

    sector1 = game_state.map.get_sector("0,-1")
    assert sector0.sect_down == sector1
    assert sector1.sect_up == sector0

    sector0 = game_state.map.get_sector("1,0")
    sector1 = game_state.map.get_sector("0,1")
    sector2 = game_state.map.get_sector("1,1")
    assert sector0.sect_up == sector2
    assert sector2.sect_down == sector0
    assert sector1.sect_right == sector2
    assert sector2.sect_left == sector1

def test_adding_new_sectors_hard():
    game_state = state.GameState()
    game_state.map.generate_map_sector("3,0")
    game_state.map.generate_map_sector("1,0")
    game_state.map.generate_map_sector("2,0")

    sector0 = game_state.map.get_sector("0,0")
    sector1 = game_state.map.get_sector("1,0")
    sector2 = game_state.map.get_sector("2,0")
    sector3 = game_state.map.get_sector("3,0")
    
    assert sector0.sect_right == sector1
    assert sector1.sect_left == sector0
    assert sector1.sect_right == sector2
    assert sector2.sect_left == sector1
    assert sector2.sect_right == sector3
    assert sector3.sect_left == sector2



def test_change_walkable():
    game_state = state.GameState()
    loc = state.EntityLocation(game_state.map.get_sector("0,0"),20,20)
    if game_state.map.check_tile_used(loc) == True:
        assert game_state.map.check_tile_used(loc) == True
        game_state.map.update_walkable(loc,False)
        assert game_state.map.check_tile_used(loc) == False

        assert game_state.map.check_tile_used(loc) == False
        game_state.map.update_walkable(loc,True)
        assert game_state.map.check_tile_used(loc) == True

def test_spawn_player():
    game_state = state.GameState()
    game_state.add_player("player1")
    assert len(game_state.players)==1
    
def test_walkable():
    game_state = state.GameState()
    game_state.add_player("player1")
    assert game_state.map.check_tile_used(game_state.players["player1"].robots[0].location) == False



