from aiohttp import web
from battleship.api import create_new_game, create_new_ship, take_turn

urls = [
    web.post("/v1/battleship/game", create_new_game),
    web.post("/v1/battleship/game/player/create_new_ship", create_new_ship),
    web.post("/v1/battleship/game/player/take_turn", take_turn),
]
