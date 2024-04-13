import json
from battleship.models.guess import GuessResult
from battleship.utils import run_game_turn, build_player_ship_details


async def connect(request, payload, ws) -> None:
    resp = {
        "type": "ack",
        "result": "success",
    }
    # Notify offense the result of their guess
    await ws.send_str(json.dumps(resp))


async def handle_take_turn(request, payload, ws) -> None:
    game_id = payload["game_id"]
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
        "guess_position_x": guess_position_x,
        "guess_position_y": guess_position_y,
    }
    # Notify offense the result of their guess
    await ws.send_str(json.dumps(resp))
    # Notify offense the result of their guess
    resp = {
        "type": "enemy_guess",
        "result": result,
        "guess_position_x": guess_position_x,
        "guess_position_y": guess_position_y,
    }
    offense_ws = next(iter(request.app["websockets"][defense_player_id]))
    await offense_ws.send_str(json.dumps(resp))
