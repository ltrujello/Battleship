import logging
from aiohttp import web
from typing import Optional
from battleship.schema import GameStatus, GuessResult

LOGGER = logging.getLogger(__name__)


async def add_player_ship(game_id: int, player_id: int, ship: int, db) -> bool:
    """
    Add a ship to the player's board.
    """
    # Check if desired ship position is within board
    ship_coordinates = calculate_ship_coordinates(
        ship["size"],
        ship["orientation"],
        ship["start_position_x"],
        ship["start_position_y"],
    )
    for coordinate in ship_coordinates:
        if not is_within_board(coordinate):
            msg = f"Attempted to place {ship=} with invalid {ship_coordinates=} as {coordinate=} is outside of board"
            LOGGER.info(msg)
            raise web.HTTPBadRequest(text=msg)

    # Check if the placement overlaps with other ships
    ships = await db.getPlayerShips(game_id=game_id, player_id=player_id)
    for placed_ship in ships:
        other_ship_coordinates = calculate_ship_coordinates(
            placed_ship["size"],
            placed_ship["orientation"],
            placed_ship["start_position_x"],
            placed_ship["start_position_y"],
        )
        for coord in other_ship_coordinates:
            if coord in ship_coordinates:
                msg = f"Attempted to place {ship=} but this overlaps with {placed_ship=} in {ships=}"
                LOGGER.info(msg)
                raise web.HTTPBadRequest(text=msg)

    await db.addShip(
        game_id=game_id,
        player_id=player_id,
        size=ship["size"],
        orientation=ship["orientation"],
        start_position_x=ship["start_position_x"],
        start_position_y=ship["start_position_y"],
    )
    return True


async def evaluate_player_guess(
    game_id: int, defense_player_id: int, guess: int, db
) -> Optional[int]:
    """
    Evaluate if the player's guess hit the ship.
    """
    ships = await db.getPlayerShips(gqme_id=game_id, player_id=defense_player_id)
    for ship in ships:
        for coord in calculate_ship_coordinates(
            ship["size"],
            ship["orientation"],
            ship["start_position_x"],
            ship["start_position_y"],
        ):
            if coord == guess:
                LOGGER.info(
                    f"In {game_id=} {defense_player_id=} ship was hit by {coord=}"
                )
                return ship["id"]
    return None


async def run_game_turn(
    game_id: int,
    guess_position_x: int,
    guess_position_y: int,
    offense_player_id: int,
    defense_player_id: int,
    db,
) -> GuessResult:
    """
    Run a single turn of the game.
    """
    # Check if game is completed or if it's the player's turn
    game = await db.getGame(game_id)
    if game["status"] == GameStatus.complete.value:
        LOGGER.info("Attempted to play but game is over")
        raise web.HTTPBadRequest(text="game is over")

    if game["current_turn"] != offense_player_id:
        LOGGER.info("Attempted to play but not players turn")
        raise web.HTTPBadRequest(text="not player's turn")

    # Evaluate guess
    guess = (guess_position_x, guess_position_y)
    ship_id: bool = await evaluate_player_guess(game_id, defense_player_id, guess, db)
    hit = False if ship_id is None else True
    await db.addGuess(guess=guess, player_id=offense_player_id, hit=hit)
    await db.incrementShipHits(id=ship_id)

    # Check if player lost
    player_lost = await check_if_player_lost(game_id, defense_player_id, db)
    if player_lost:
        return GuessResult.victory

    # If not, rotate offense, defense
    await db.updateGame(game_id=game_id, current_turn=defense_player_id)
    if hit:
        return GuessResult.hit
    return GuessResult.miss


async def check_if_player_lost(game_id: int, player_id: int, db) -> bool:
    """
    Check if the player has lost.
    """
    ships = await db.getPlayerShips(game_id=game_id, player_id=player_id)
    for ship in ships:
        if ship["size"] != ship["hits"]:
            return False
    return True


def calculate_ship_coordinates(
    size: int, orientation: int, start_position_x: int, start_position_y: int
) -> list[tuple[int, int]]:
    """
    Calculate the coordinates of the ship.
    """
    coordinates = []
    for i in range(size):
        if orientation == "horizontal":
            point = (start_position_x + i, start_position_y)
        else:  # orientation == "vertical"
            point = (start_position_x, start_position_y + i)
        coordinates.append(point)
    return coordinates


def is_within_board(point: tuple[int, int]) -> bool:
    """
    Determine if the coordinates are within the board.
    """
    x = point[0]
    y = point[1]
    return 0 <= x <= 9 and 0 <= y <= 9
