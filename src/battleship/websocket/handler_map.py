from battleship.websocket.game_handlers import (
    handle_take_turn,
    connect,
    handle_create_new_ship,
    handle_fetch_game_details,
)


handlers = {
    "take_turn": handle_take_turn,
    "create_new_ship": handle_create_new_ship,
    "fetch_game_details": handle_fetch_game_details,
    "connect": connect,
}
