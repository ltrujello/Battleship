import pytest
from battleship.utils import (
    calculate_ship_coordinates,
    evaluate_player_guess,
    check_if_player_lost,
)


def test_get_ship_coordinates_horizontal():
    orientation = "horizontal"
    expected_coordinates = [(0, 0), (1, 0), (2, 0)]
    actual_coordinates = calculate_ship_coordinates(3, orientation, 0, 0)
    assert actual_coordinates == expected_coordinates


def test_get_ship_coordinates_vertical():
    orientation = "vertical"
    expected_coordinates = [(0, 0), (0, 1), (0, 2)]
    actual_coordinates = calculate_ship_coordinates(3, orientation, 0, 0)
    assert actual_coordinates == expected_coordinates


@pytest.mark.asyncio
async def test_check_if_player_lost(mock_db):
    ships = mock_db.get_player_ships.return_value
    ships[0].hits = ships[0].size
    game_id = 1
    player_id = 1
    player_lost = await check_if_player_lost(
        game_id=game_id, player_id=player_id, db=mock_db
    )
    assert player_lost is True


@pytest.mark.asyncio
async def test_check_if_player_lost_false(mock_db):
    ships = mock_db.get_player_ships.return_value
    ships[0].hits = ships[0].size - 1
    game_id = 1
    player_id = 1
    player_lost = await check_if_player_lost(
        game_id=game_id, player_id=player_id, db=mock_db
    )
    assert player_lost is False


@pytest.mark.asyncio
async def test_evaluate_player_guess_hit(mock_db, mock_ship):
    game_id = 1
    defense_player_id = 1
    guess = (0, 0)
    mock_ship.start_position_x = 0
    mock_ship.start_position_y = 0
    mock_db.get_player_ships.return_value = [mock_ship]
    hit = await evaluate_player_guess(game_id, defense_player_id, guess, mock_db)
    assert hit is not None


@pytest.mark.asyncio
async def test_evaluate_player_guess_miss(mock_db, mock_ship):
    game_id = 1
    defense_player_id = 1
    guess = (5, 5)
    mock_ship.start_position_x = 0
    mock_ship.start_position_y = 0
    mock_db.get_player_ships.return_value = [mock_ship]
    hit = await evaluate_player_guess(game_id, defense_player_id, guess, mock_db)
    assert hit is None
