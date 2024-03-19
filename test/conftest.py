import pytest
import copy
from aiohttp import web
from battleship.api.urls import urls
from battleship.schema import server_response_for_validation_error
from battleship.models.player import Player
from battleship.models.game import Game, GameStatus
from battleship.models.ship import Ship, ShipOrientation
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec
from unittest.mock import AsyncMock


@pytest.fixture
def mock_db(mock_game, mock_player_ships):
    db = AsyncMock(
        add_game=AsyncMock(return_value=1),
        get_game=AsyncMock(return_value=mock_game),
        add_guess=AsyncMock(),
        add_ship=AsyncMock(),
        update_game=AsyncMock(),
        get_player_ships=AsyncMock(return_value=mock_player_ships),
    )
    return db


@pytest.fixture
def mock_player_1():
    player = {
        "id": 1,
        "first_name": "foo",
        "last_name": "bar",
    }
    return Player(**player)


@pytest.fixture
def mock_player_2():
    player = {
        "id": 2,
        "first_name": "foo",
        "last_name": "bar",
    }
    return Player(**player)


@pytest.fixture
def mock_game(mock_player_1, mock_player_2):
    game = {
        "player_1_id": mock_player_1.id,
        "player_2_id": mock_player_2.id,
        "current_player_id": mock_player_1.id,
        "status": GameStatus.in_progress.value,
    }
    return Game(**game)


@pytest.fixture
def mock_ship():
    ship = {
        "id": 1,
        "orientation": ShipOrientation.horizontal.value,
        "start_position_x": 0,
        "start_position_y": 0,
        "size": 5,
    }
    return Ship(**ship)


@pytest.fixture
def mock_player_ships(mock_ship):
    ship = {
        "id": 1,
        "orientation": ShipOrientation.horizontal.value,
        "start_position_x": 5,
        "start_position_y": 5,
        "size": 5,
        "hits": 0,
    }
    return [Ship(**ship)]


@pytest.fixture
def create_new_player_request():
    return {
        "first_name": "foo",
        "last_name": "bar",
        "email": "foo@bar.com",
    }


@pytest.fixture
def turn_request():
    return {
        "game_id": 1,
        "offense_player_id": 1,
        "defense_player_id": 2,
        "guess_position_x": 0,
        "guess_position_y": 0,
    }


@pytest.fixture
def add_ship_request():
    return {
        "game_id": 1,
        "player_id": 1,
        "ship": {
            "start_position_x": 1,
            "start_position_y": 2,
            "size": 5,
            "orientation": "horizontal",
        },
    }


@pytest.fixture
def new_game_request():
    return {
        "player_1_id": 1,
        "player_2_id": 2,
        "initial_player": 1,
    }


@pytest.fixture
def battleship_client(event_loop, aiohttp_client, mock_db):
    app = web.Application(middlewares=[validation_middleware])
    app["battleship_db"] = mock_db
    app.add_routes(urls)
    setup_aiohttp_apispec(app, error_callback=server_response_for_validation_error)
    return event_loop.run_until_complete(aiohttp_client(app))
