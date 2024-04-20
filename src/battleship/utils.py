import logging
from aiohttp import web
from typing import Optional
from collections import defaultdict
from battleship.schema import GameStatus
from battleship.models.ship import Ship
from battleship.models.guess import Guess, GuessResult

LOGGER = logging.getLogger(__name__)


async def add_player_ship(game_id: int, player_id: int, ship: dict, db) -> bool:
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
                msg = (
                    f"Attempted to place {ship=} but this overlaps with {placed_ship=}"
                )
                LOGGER.info(msg)
                raise web.HTTPBadRequest(text=msg)

    ship = Ship(
        game_id=game_id,
        player_id=player_id,
        size=ship["size"],
        orientation=ship["orientation"],
        start_position_x=ship["start_position_x"],
        start_position_y=ship["start_position_y"],
        hits=0,
    )
    await db.add_ship(ship)
    return ship


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
        LOGGER.info(
            f"Player {offense_player_id=} attempted to play, but it's {game.current_player_id=} turn"
        )
        raise web.HTTPBadRequest(text="not player's turn")

    # Evaluate guess
    guess_coords = (guess_position_x, guess_position_y)
    ship_id: Optional[int] = await evaluate_player_guess(
        game_id, defense_player_id, guess_coords, db
    )
    hit: bool = False if ship_id is None else True

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
        offense_player_id=offense_player_id,
        ship_id=ship_id,
        position_x=guess_position_x,
        position_y=guess_position_y,
        result=result,
    )
    await db.add_guess(guess)
    return result


async def build_player_game_details(game_id: int, player_id: int, db) -> dict:
    """
    Returns a dictionary detailing a player's ships (coordinates, hits) and their
    guesses so far.
    """
    game_details: dict = await db.get_game_details(game_id, player_id)
    game = {
        "player_1_id": game_details["game"].player_1_id,
        "player_2_id": game_details["game"].player_2_id,
        "current_player_id": game_details["game"].current_player_id,
        "status": game_details["game"].status,
    }
    player_ships = []
    for ship in game_details["player_ships"]:
        player_ships.append(
            {
                "size": ship.size,
                "orientation": ship.orientation,
                "start_position_x": ship.start_position_x,
                "start_position_y": ship.start_position_y,
            }
        )

    player_guesses = []
    for guess in game_details["player_guesses"]:
        player_guesses.append(
            {
                "position_x": guess.position_x,
                "position_y": guess.position_y,
                "result": guess.result,
            }
        )

    enemy_guesses = []
    for guess in game_details["enemy_guesses"]:
        enemy_guesses.append(
            {
                "position_x": guess.position_x,
                "position_y": guess.position_y,
                "result": guess.result,
            }
        )

    return {
        "game": game,
        "player_ships": player_ships,
        "player_guesses": player_guesses,
        "enemy_guesses": enemy_guesses,
    }


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
    size: int, orientation: str, start_position_x: int, start_position_y: int
) -> list[tuple[int, int]]:
    """
    Calculate the coordinates of the ship.
    """
    if orientation == "horizontal":
        return [(start_position_x + i, start_position_y) for i in range(size)]
    return [(start_position_x, start_position_y + i) for i in range(size)]


def is_within_board(point: tuple[int, int]) -> bool:
    """
    Determine if the coordinates are within the board.
    """
    x = point[0]
    y = point[1]
    return 0 <= x <= 9 and 0 <= y <= 9


async def get_player_games(player_id, db):
    games = await db.get_player_games(player_id=player_id)
    games_list: list[dict] = []
    for game in games:
        games_list.append(
            {
                "game_id": game.id,
                "players": [game.player_1_id, game.player_2_id],
                "status": game.status,
                "current_player_id": game.current_player_id,
            }
        )
    return games_list
