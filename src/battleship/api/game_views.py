import aiohttp_apispec
from aiohttp import web
from battleship.schema import CreateNewGameRequest, TakeTurnRequest
from battleship.models.game import Game
from battleship.models.guess import GuessResult
from battleship.utils import run_game_turn


@aiohttp_apispec.request_schema(CreateNewGameRequest)
async def create_new_game(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    player_1_id = payload["player_1_id"]
    player_2_id = payload["player_2_id"]
    initial_player = payload["initial_player"]

    game = Game(
        player_1_id=player_1_id,
        player_2_id=player_2_id,
        current_player_id=initial_player,
        status="in_progress",
    )
    game = await db.add_game(game)

    return web.json_response({"game_id": game.id})


@aiohttp_apispec.request_schema(TakeTurnRequest)
async def take_turn(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    game_id = payload["game_id"]
    guess_position_x = payload["guess_position_x"]
    guess_position_y = payload["guess_position_y"]
    offense_player_id = payload["offense_player_id"]
    defense_player_id = payload["defense_player_id"]

    result: GuessResult = await run_game_turn(
        game_id,
        guess_position_x,
        guess_position_y,
        offense_player_id,
        defense_player_id,
        db,
    )

    response = {"current_player_id": defense_player_id, "result": result.value}
    return web.json_response(response)
