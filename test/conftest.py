import pytest
import copy
from aiohttp import web
from battleship.urls import urls
from battleship.schema import (
    GameStatus,
    ShipOrientation,
    server_response_for_validation_error,
)
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec
from unittest.mock import AsyncMock


@pytest.fixture
def mock_db(mock_game, mock_player_ships):
    db = AsyncMock(
        addGame=AsyncMock(return_value=1),
        getGame=AsyncMock(return_value=mock_game),
        addGuess=AsyncMock(),
        addShip=AsyncMock(),
        updateGame=AsyncMock(),
        getPlayerShips=AsyncMock(return_value=mock_player_ships),
    )
    return db


@pytest.fixture
def mock_game():
    return {
        "player_1_id": 1,
        "player_2_id": 2,
        "current_turn": 1,
        "status": GameStatus.in_progress.value,
    }


@pytest.fixture
def mock_ship():
    return {
        "orientation": ShipOrientation.horizontal.value,
        "start_position_x": 0,
        "start_position_y": 0,
        "size": 5,
    }


@pytest.fixture
def mock_player_ships(mock_ship):
    return [
        {
            "id": 1,
            "orientation": ShipOrientation.horizontal.value,
            "start_position_x": 5,
            "start_position_y": 5,
            "size": 5,
            "hits": 0,
        }
    ]


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
