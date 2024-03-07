import pytest


@pytest.mark.asyncio
async def create_new_ship(battleship_client, mock_ship, new_game_request):
    ret = await battleship_client.post("v1/battleship/game", json=new_game_request)
    assert ret.status == 200


@pytest.mark.asyncio
async def test_add_new_ship(battleship_client, mock_ship):
    mock_ship["start_position_x"] = 1
    mock_ship["start_position_y"] = 2
    payload = {
        "game_id": 1,
        "player_id": 1,
        "ship": mock_ship,
    }
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=payload
    )
    assert ret.status == 200


@pytest.mark.asyncio
async def test_add_new_ship_outside_range(battleship_client, mock_ship):
    mock_ship["start_position_x"] = 9
    mock_ship["start_position_y"] = 9
    payload = {
        "game_id": 1,
        "player_id": 1,
        "ship": mock_ship,
    }
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=payload
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_add_new_ship_overlaps(battleship_client, mock_ship):
    mock_ship["start_position_x"] = 5
    mock_ship["start_position_y"] = 5
    payload = {
        "game_id": 1,
        "player_id": 1,
        "ship": mock_ship,
    }
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=payload
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_turn(battleship_client, mock_ship, turn_request):
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200


@pytest.mark.asyncio
async def test_turn_game_completed(battleship_client, mock_ship, mocker, turn_request):
    mocker.patch("battleship.utils.check_if_player_lost", return_value=True)
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "victory"


@pytest.mark.asyncio
async def test_turn_miss(battleship_client, mock_ship, mocker, turn_request):
    mocker.patch("battleship.utils.check_if_player_lost", return_value=False)
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "miss"


@pytest.mark.asyncio
async def test_turn(battleship_client, mock_ship, turn_request):
    turn_request["guess_position_x"] = 5
    turn_request["guess_position_y"] = 5
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "hit"
