import logging
import aiohttp_apispec
from aiohttp import web
from battleship.schema import CreateNewPlayerRequest
from battleship.models.player import Player

LOGGER = logging.getLogger(__name__)


@aiohttp_apispec.request_schema(CreateNewPlayerRequest)
async def create_new_player(request):
    db = request.app["battleship_db"]
    payload = request["data"]

    first_name = payload["last_name"]
    last_name = payload["last_name"]
    email = payload["email"]

    player = Player(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    player = await db.add_player(player)

    LOGGER.info(f"Created {player.id=}")
    return web.json_response({"player_id": player.id})
