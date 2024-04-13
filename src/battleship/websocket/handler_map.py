from battleship.websocket.game_handlers import handle_take_turn, connect

handlers = {
    "take_turn": handle_take_turn,
    "connect": connect,
}
