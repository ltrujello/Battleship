import aiohttp_apispec
from aiohttp import web
from battleship.schema import (
    CreateNewGameRequest,
    TakeTurnRequest,
    GetPlayerBoard,
    PlayerBoard,
    PlayerId,
)
from battleship.models.game import Game
from battleship.models.guess import GuessResult
from battleship.utils import (
    run_game_turn,
    get_player_games,
    build_player_game_details,
)


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


@aiohttp_apispec.querystring_schema(GetPlayerBoard)
@aiohttp_apispec.response_schema(PlayerBoard)
async def get_game_details_for_player(request):
    params = request["querystring"]
    game_id = params["game_id"]
    player_id = params["player_id"]
    db = request.app["battleship_db"]

    game_details: dict = await build_player_game_details(game_id, player_id, db)

    return web.json_response(game_details)


@aiohttp_apispec.querystring_schema(PlayerId)
# @aiohttp_apispec.response_schema(PlayerBoard)
async def fetch_player_games(request):
    params = request["querystring"]
    player_id = params["player_id"]
    db = request.app["battleship_db"]

    games: list = await get_player_games(player_id, db)

    return web.json_response({"games": games})


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
