import os
import aiohttp
import asyncio
import json
from aiohttp import ClientSession
from board import Board

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
BASE_URL = f"http://{HOST}:{PORT}"
API_URL = f"{BASE_URL}/v1/battleship"
WEBSOCKET_URL = f"{BASE_URL}/ws"


async def fetch_player_games(user_id, session):
    params = {"player_id": user_id}
    async with session.get(f"{API_URL}/player/games", params=params) as response:
        games = await response.json()
    return games


async def fetch_game_details(user_id, game_id, session):
    params = {"game_id": game_id, "player_id": user_id}
    async with session.get(f"{API_URL}/game/player/details", params=params) as response:
        games = await response.json()
    return games


class BattleshipTerminal:
    """
    A class to run a battleship game in the terminal.
    """

    def __init__(self, player_id: int, game_id: int, session: ClientSession, websocket):
        self.player_id = player_id
        self.game_id = game_id
        self.board = Board()
        self.session = session
        self.websocket = websocket

    async def send_msg(self, payload: dict):
        payload["user_id"] = self.player_id
        payload["game_id"] = self.game_id
        await self.websocket.send_json(payload)

    async def load_game(self):
        data = await fetch_game_details(self.player_id, self.game_id, self.session)
        print(f"Game details {data=}")
        player_ships: list[dict] = data["player_ships"]
        player_guesses: list[dict] = data["player_guesses"]
        enemy_guesses: list[dict] = data["enemy_guesses"]

        self.board.add_ships(player_ships)
        self.board.add_players_guess_history(player_guesses)
        self.board.add_enemys_guess_history(enemy_guesses)
        self.draw_board()
        await self.send_msg({"action": "connect"})

    def draw_board(self):
        self.board.draw_board()

    async def create_new_ship(
        self, size: int, orientation: str, start_position_x: int, start_position_y: int
    ):
        payload = {
            "action": "create_new_ship",
            "ship": {
                "size": size,
                "orientation": orientation,
                "start_position_x": start_position_x,
                "start_position_y": start_position_y,
            },
        }
        await self.send_msg(payload)

    async def take_turn(self, guess_position_x: int, guess_position_y: int):
        payload = {
            "action": "take_turn",
            "position_x": guess_position_x,
            "position_y": guess_position_y,
        }
        await self.send_msg(payload)

    async def handle_guess_result(self, payload) -> None:
        guesses = [
            {
                "result": payload["result"],
                "position_x": payload["position_x"],
                "position_y": payload["position_y"],
            }
        ]
        self.board.add_players_guess_history(guesses)

    async def handle_incoming_enemy_guess_result(self, payload) -> None:
        guesses = [
            {
                "result": payload["result"],
                "position_x": payload["position_x"],
                "position_y": payload["position_y"],
            }
        ]
        self.board.add_enemys_guess_history(guesses)

    async def handle_create_new_ship_result(self, payload) -> None:
        if payload["result"] == "failure":
            print("Creating a new ship failed")
            print(f"{payload['msg']=}")
            return

        ships = [
            {
                "ship_size": payload["ship_size"],
                "orientation": payload["orientation"],
                "start_position_x": payload["start_position_x"],
                "start_position_y": payload["start_position_y"],
            }
        ]
        self.board.add_ships(ships)


async def main():
    user_id = input("Please type your user id.")
    user_id = int(user_id)
    print("Thank you! These are the games you have available.")
    session = ClientSession()
    games = await fetch_player_games(user_id, session)
    print(json.dumps(games, indent=4))
    game_id = input("Which game would you like to play?")
    game_id = int(game_id)

    async with session.ws_connect(WEBSOCKET_URL) as ws:
        battleship_game = BattleshipTerminal(
            player_id=user_id, game_id=game_id, session=session, websocket=ws
        )
        await battleship_game.load_game()
        # Listen
        async for msg in ws:
            os.system("cls" if os.name == "nt" else "clear")

            print("Message received from server:", msg)
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break
            payload = msg.json()
            if payload["type"] == "enemy_guess":
                await battleship_game.handle_incoming_enemy_guess_result(payload)
            elif payload["type"] == "guess_result":
                await battleship_game.handle_guess_result(payload)
            elif payload["type"] == "new_ship":
                await battleship_game.handle_create_new_ship_result(payload)
            else:
                print(f"Received unexpected {payload=}")

            battleship_game.draw_board()

    await session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
