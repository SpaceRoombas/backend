#Roombalang Documentation
## Keywords and Syntax
### let
```let i = 5```

Sets the variable i to 5, however `let` is completely optional, the below has the same effect.

```i = 5```
### if
The below prints "1".

```
if(true)
    print(1)
else
    print(0)
```

### while
The below prints numbers 1-10.

```
i = 1
while(i <= 10){
    print(i) i++
}
```

### for
The below prints numbers 5-9.

```
for(i=5; i<10; i++){
    print(i)
}
```

### fun and return
The below declares the function `foo(a, b)` that returns a+b, then calls it.

```
fun foo(a, b){
    bar = a + b
    return bar
}

foo()
```

## Operators
|Operator|Description|
|---|---|
|+|addition|
|-|subtraction (also negation)|
|*|multiplication|
|/|division|
|\|modulus|
|**|exponentiation|
|==|equality check|
|!=|not equal to|
|\>=|greater than or equal to|
|<=|less than or equal to|
|\>|greater than|
|<|less than|
|!|not|
|&&|and|
|&#124;&#124;|or|
|^|xor|
|++|Increments an expression.|
|--|Decrements an expression.|

Note: Many of the above operators are also available in their assignment forms

e.g. +=, *=, -=, etc.
## Built-in Constants
|Constant|Description|
|---|---|
|true  | True.                           |
|false | False.                          |
|pi    | The first 12 digits of pi.      |
|north | Direction constant, equal to 0. |
|east  | Direction constant, equal to 1. |
|south | Direction constant, equal to 2. |
|west  | Direction constant, equal to 3. |

## Built-in Functions
### Movement
#### move_north()
Moves the robot north.
#### move_east()
Moves the robot east.
#### move_south()
Moves the robot south
#### move_west()
Moves the robot west.
#### move(dir)
Takes in a direction and moves the robot in that direction.

### Mining
#### mine(dir)
Takes in a direction and mines in that direction, getting 1 resource if the tile is a resource.

### Terraforming
#### terraform()
Increases the players score by 1 and consumes 4 resources.

### Replication
#### reproduce()
Takes in a direction and reproduces in that direction consuming 1 resource.

### Sensing
#### look(dir)
Takes in a direction and returns the tile there, -1 if a robot is there, or -2 if it is outside the map bounds.
#### resources()
Returns the number of resources the robot currently has.

### Utility
#### rand_dir()
Returns a random direction.