import json
import logging
from aiohttp import web
from battleship.models.guess import GuessResult
from battleship.utils import (
    run_game_turn,
    add_player_ship,
    build_player_game_details,
    move_ship,
)

LOGGER = logging.getLogger(__name__)


async def connect(request, payload, ws) -> None:
    resp = {
        "type": "ack",
        "result": "success",
    }
    # Notify offense the result of their guess
    await ws.send_json(resp)


async def handle_take_turn(request, payload, ws) -> None:
    game_id = payload["game_id"]
    player_id = payload["player_id"]
    offense_player_id = payload["player_id"]
    defense_player_id = payload["defense_player_id"]
    guess_position_x = payload["guess_position_x"]
    guess_position_y = payload["guess_position_y"]

    db_session = request.app["battleship_db"]
    result: GuessResult = await run_game_turn(
        game_id,
        guess_position_x,
        guess_position_y,
        offense_player_id,
        defense_player_id,
        db_session,
    )
    resp = {
        "type": "guess_result",
        "result": result,
        "position_x": guess_position_x,
        "position_y": guess_position_y,
    }
    # Notify offense the result of their guess
    websockets = list(request.app["websockets"][player_id])
    for active_ws in websockets:
        LOGGER.info(f"Notifying {offense_player_id=}")
        try:
            await active_ws.send_json(resp)
        except ConnectionResetError:
            request.app["websockets"][player_id].remove(active_ws)

    # Notify defense the result of the player's guess
    resp = {
        "type": "enemy_guess",
        "result": result,
        "position_x": guess_position_x,
        "position_y": guess_position_y,
    }
    websockets = list(request.app["websockets"][defense_player_id])
    for active_ws in websockets:
        LOGGER.info(f"Notifying {defense_player_id=}")
        try:
            await active_ws.send_json(resp)
        except ConnectionResetError:
            request.app["websockets"][player_id].remove(active_ws)


async def handle_create_new_ship(request, payload, ws) -> None:
    player_id = payload["player_id"]
    game_id = payload["game_id"]
    ship = payload["ship"]
    db_session = request.app["battleship_db"]
    try:
        new_ship = await add_player_ship(game_id, player_id, ship, db_session)
    except web.HTTPException as e:
        resp = {
            "type": "new_ship",
            "result": "failure",
            "msg": e.text,
        }
        await ws.send_json(resp)
        return

    resp = {
        "type": "new_ship",
        "result": "success",
        "ship_details": {
            "ship_id": new_ship.id,
            "ship_size": new_ship.size,
            "orientation": new_ship.orientation,
            "start_position_x": new_ship.start_position_x,
            "start_position_y": new_ship.start_position_y,
        },
    }
    websockets = list(request.app["websockets"][player_id])
    for active_ws in websockets:
        try:
            await active_ws.send_json(resp)
        except ConnectionResetError:
            request.app["websockets"][player_id].remove(active_ws)


async def handle_move_ship(request, payload, ws) -> None:
    player_id = payload["player_id"]
    game_id = payload["game_id"]
    ship_id = payload["ship_id"]
    start_position_x = payload["start_position_x"]
    start_position_y = payload["start_position_y"]

    db_session = request.app["battleship_db"]
    try:
        ship = await move_ship(
            game_id, player_id, ship_id, start_position_x, start_position_y, db_session
        )
    except web.HTTPException as e:
        resp = {
            "type": "move_ship",
            "result": "failure",
            "msg": e.text,
        }
        await ws.send_json(resp)
        return

    resp = {
        "type": "move_ship",
        "result": "success",
        "ship_details": {
            "ship_id": ship.id,
            "ship_size": ship.size,
            "orientation": ship.orientation,
            "start_position_x": ship.start_position_x,
            "start_position_y": ship.start_position_y,
        },
    }

    websockets = list(request.app["websockets"][player_id])
    for active_ws in websockets:
        try:
            await active_ws.send_json(resp)
        except ConnectionResetError:
            request.app["websockets"][player_id].remove(active_ws)


async def handle_fetch_game_details(request, payload, ws) -> None:
    player_id = payload["player_id"]
    game_id = payload["game_id"]
    db_session = request.app["battleship_db"]

    resp = await build_player_game_details(
        game_id=game_id, player_id=player_id, db=db_session
    )

    await ws.send_json(resp)
