from data import state


def test_expand_map(): #checks to see if map has walkable value and value for there being a wall/type of tile...Right now check if they are the same
    sector1 = state.MapSector("iddeeznuts")
    print(sector1.land_map)
    for row in sector1.land_map:
        for tile in row:
            assert tile[0] == True and tile[1] == 0 or tile[0] == False and tile[1] == 1

def test_sector_parsor():
    sector_id = "0,0"
    assert state.MapState.parse_id(sector_id) == (0,0)
    sector_id = "203,192"
    assert state.MapState.parse_id(sector_id) == (203,192)
    sector_id = "-203,192"
    assert state.MapState.parse_id(sector_id) == (-203,192)
    sector_id = "-203,-192"
    assert state.MapState.parse_id(sector_id) == (-203,-192)
    sector_id = "203,-192"
    assert state.MapState.parse_id(sector_id) == (203,-192)

def test_sectorid_fromindex():
    x=0
    y=0
    assert state.MapState.form_sector_id(x,y) =="0,0"
    x=-1
    y=-2131
    assert state.MapState.form_sector_id(x,y) =="-1,-2131"
    x=12
    y=-2131
    assert state.MapState.form_sector_id(x,y) =="12,-2131"

def test_new_sector():
    game_state = state.GameState()
    assert game_state.map.sector_count() == 1
    game_state.map.generate_map_sector("0,0")
    assert game_state.map.sector_count() == 1
    game_state.map.generate_map_sector("1,0")
    assert game_state.map.sector_count() == 2

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
    
    
def test_walkable():
    game_state = state.GameState()
    game_state.add_player("player1")
    assert game_state.map.check_tile_used(game_state.players["player1"].robots[0].location) == False




