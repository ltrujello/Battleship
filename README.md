# Battleship

Aiohttp server to support online multiplayer battleship.

## Possible DB Schema

### Enums
```
GameStatus: in_progress, completed
GuessResult: hit, miss, victory
ShipOrientation: horizontal, vertical
```

### Tables
#### Game
Game: Stores information about each game session.
```
Column: 
id (primary key)
player_1_id (foreign key) 
player_2_id (foreign key) 
current_player (foreign key) 
status (GameStatus enum)
```

#### Player
Player: Stores player information.
```
Columns: 
id (primary key), 
first_name (str)
last_name (str)
email (str)
```

#### Ship
Ship: Stores information about the ships placed on the board.
```
Columns: 
id (primary key) 
game_id (int)
player_id (int)
orientation (Orientation enum)
start_position_x (int)
start_position_y (int) 
size (int) 
hits (int)
```
#### Guess
Guess: Records the details of each player's guesses.
```
id (primary key)
game_id (foreign key)
player_id (foreign key)
position_x (int) 
position_y (int) 
result (GuessResult enum)
```
