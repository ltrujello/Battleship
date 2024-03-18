import logging
from aiohttp import web
from typing import Optional
from battleship.schema import GameStatus
from battleship.models.ship import Ship
from battleship.models.guess import Guess, GuessResult

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
    ships = await db.get_player_ships(game_id=game_id, player_id=player_id)
    for placed_ship in ships:
        other_ship_coordinates = calculate_ship_coordinates(
            placed_ship.size,
            placed_ship.orientation,
            placed_ship.start_position_x,
            placed_ship.start_position_y,
        )
        for coord in other_ship_coordinates:
            if coord in ship_coordinates:
                msg = f"Attempted to place {ship=} but this overlaps with {placed_ship=} in {ships=}"
                LOGGER.info(msg)
                raise web.HTTPBadRequest(text=msg)

    ship = Ship(
        game_id=game_id,
        player_id=player_id,
        size=ship["size"],
        orientation=ship["orientation"],
        start_position_x=ship["start_position_x"],
        start_position_y=ship["start_position_y"],
    )
    await db.add_ship(ship)
    return True


async def evaluate_player_guess(
    game_id: int, defense_player_id: int, guess: int, db
) -> Optional[int]:
    """
    Evaluate if the player's guess hit the ship.
    """
    ships = await db.get_player_ships(game_id=game_id, player_id=defense_player_id)
    for ship in ships:
        for coord in calculate_ship_coordinates(
            ship.size,
            ship.orientation,
            ship.start_position_x,
            ship.start_position_y,
        ):
            if coord == guess:
                LOGGER.info(
                    f"In {game_id=} {defense_player_id=} {ship.id=} was hit by {coord=}"
                )
                return ship.id
    LOGGER.info(f"In {game_id=} {defense_player_id=} ship was not hit by {coord=}")
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
    game = await db.get_game(game_id)
    if game.status == GameStatus.complete.value:
        LOGGER.info("Attempted to play but game is over")
        raise web.HTTPBadRequest(text="game is over")

    if game.current_player_id != offense_player_id:
        LOGGER.info("Attempted to play but not players turn")
        raise web.HTTPBadRequest(text="not player's turn")

    # Evaluate guess
    guess_coords = (guess_position_x, guess_position_y)
    ship_id: int = await evaluate_player_guess(
        game_id, defense_player_id, guess_coords, db
    )
    hit = False if ship_id is None else True

    if hit:
        await db.increment_ship_hits(ship_id=ship_id)
        # Check if player lost
        player_lost = await check_if_player_lost(game_id, defense_player_id, db)
        if player_lost:
            LOGGER.info(
                f"{offense_player_id=} hit {defense_player_id=} and won with {guess_coords=}"
            )
            result = GuessResult.victory
        else:
            LOGGER.info(
                f"{offense_player_id=} hit {defense_player_id=} with {guess_coords=}"
            )
            result = GuessResult.hit
    else:
        LOGGER.info(
            f"{offense_player_id=} missed {defense_player_id=} with {guess_coords=}"
        )
        result = GuessResult.miss

    if result in [GuessResult.hit.value, GuessResult.miss.value]:
        await db.update_game(
            game_id=game_id, updates={"current_player_id": defense_player_id}
        )

    guess = Guess(
        game_id=game_id,
        player_id=offense_player_id,
        position_x=guess_position_x,
        position_y=guess_position_y,
        result=result,
    )
    await db.add_guess(guess)
    return result


async def check_if_player_lost(game_id: int, player_id: int, db) -> bool:
    """
    Check if the player has lost.
    """
    ships = await db.get_player_ships(game_id=game_id, player_id=player_id)
    for ship in ships:
        if ship.size != ship.hits:
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
