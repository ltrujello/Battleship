import aiohttp_apispec
from aiohttp import web
from battleship.schema import (
    CreateNewGameRequest,
    AddNewShipRequest,
    TakeTurnRequest,
    GuessResult,
)
from battleship.utils import add_player_ship, run_game_turn


@aiohttp_apispec.request_schema(CreateNewGameRequest)
async def create_new_game(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    player_1_id = payload["player_1_id"]
    player_2_id = payload["player_2_id"]
    initial_player = payload["initial_player"]

    game_id: int = await db.addGame(
        player_1_id=player_1_id, player_2_id=player_2_id, current_turn=initial_player
    )
    return web.json_response({"game_id": game_id})


@aiohttp_apispec.request_schema(AddNewShipRequest)
async def create_new_ship(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    player_id = payload["player_id"]
    game_id = payload["game_id"]
    ship = payload["ship"]

    await add_player_ship(game_id, player_id, ship, db)
    return web.HTTPOk()


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
