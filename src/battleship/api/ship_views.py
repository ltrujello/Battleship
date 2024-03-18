import aiohttp_apispec
from aiohttp import web
from battleship.schema import AddNewShipRequest
from battleship.utils import add_player_ship


@aiohttp_apispec.request_schema(AddNewShipRequest)
async def create_new_ship(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    player_id = payload["player_id"]
    game_id = payload["game_id"]
    ship = payload["ship"]

    await add_player_ship(game_id, player_id, ship, db)
    return web.HTTPOk()
