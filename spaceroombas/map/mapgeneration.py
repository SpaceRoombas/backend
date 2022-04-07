import random

def Make_World(x_range,y_range,rand):
    world_map = []
    for y in range(y_range):
        world_map.append([])
        for x in range(x_range):
            world_map[y].append(1) if random.random()<rand else world_map[y].append(0)
    return world_map


#count # of neighbors in x,y cordinate
def Count_Neighbors(world,x,y,sides):
    count = 0
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if True!=(x+i < 0 or x+i >= len(world) or y+j<0 or y+j>= len(world[0])) : # checks to see if its a live tile and if its out of bound
                if world[x+i][y+j] == 1:
                    count +=1
            elif sides: # if sides is true count an out of bound as true
                count +=1
                
    return count - world[x][y]

#run one step of the simulation
def Update_World(old_world,stay,birth,sides): # stay is number of neighbors needed to stay birth is number of neihbors needed to make a new one
    new_world = [row[:] for row in old_world]
    for i in range(len(old_world)):
        for j in range(len(old_world[i])):
            if old_world[i][j]: #if alive
                if Count_Neighbors(old_world,i,j,sides)<stay: #if tile doesnt have enough neighbors remove it
                    new_world[i][j] = 0
            else: #if dead
                if Count_Neighbors(old_world,i,j,sides) >=birth:#if tile has enough neighbors, spawn it
                    new_world[i][j] = 1
    return new_world

#x,y = size of world. rand = chance of a tile spawning initally.
# stay = # of neighbors needed to keep a tile alive. birth = number of tiles to turn a dead tile alive.
# steps = number of steps. sides = if count sides as live
def Run_Simulation(x,y,rand,stay,birth,steps,sides = False):
    world = Make_World(x,y,rand)
    for i in range(steps):
        world = Update_World(world,stay,birth,sides)
    return world
def Append_Walkable(prev_map):
    new_map = []
    for y in range(len(prev_map)):
        new_map.append([])
        for x in range(len(prev_map[0])):
            if prev_map[x][y] == 1:
                new_map[y].append([False,prev_map[x][y]])
            else:
                new_map[y].append([True,prev_map[x][y]])
    return new_map

def generate():
    return Append_Walkable(Run_Simulation(50,50,.4,4,6,5)) #2gold clusters 
