from aiohttp import web
from battleship.api.game_views import create_new_game, take_turn
from battleship.api.ship_views import create_new_ship

urls = [
    web.post("/v1/battleship/game", create_new_game),
    web.post("/v1/battleship/game/player/create_new_ship", create_new_ship),
    web.post("/v1/battleship/game/player/take_turn", take_turn),
]
