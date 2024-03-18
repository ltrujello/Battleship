import pytest


@pytest.mark.asyncio
async def create_new_ship(battleship_client, new_game_request):
    ret = await battleship_client.post("v1/battleship/game", json=new_game_request)
    assert ret.status == 200


@pytest.mark.asyncio
async def test_add_new_ship(battleship_client, add_ship_request):
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=add_ship_request
    )
    assert ret.status == 200


@pytest.mark.asyncio
async def test_add_new_ship_outside_range(battleship_client, add_ship_request):
    add_ship_request["ship"]["start_position_x"] = 9
    add_ship_request["ship"]["start_position_y"] = 9
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=add_ship_request
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_add_new_ship_overlaps(battleship_client, add_ship_request):
    add_ship_request["ship"]["start_position_x"] = 5
    add_ship_request["ship"]["start_position_y"] = 5
    ret = await battleship_client.post(
        "v1/battleship/game/player/create_new_ship", json=add_ship_request
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_turn(battleship_client, turn_request):
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200


@pytest.mark.asyncio
async def test_turn_hit(battleship_client, turn_request):
    turn_request["guess_position_x"] = 5
    turn_request["guess_position_y"] = 5
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "hit"


@pytest.mark.asyncio
async def test_turn_game_completed(battleship_client, mocker, turn_request):
    turn_request["guess_position_x"] = 5
    turn_request["guess_position_y"] = 5
    mocker.patch("battleship.utils.check_if_player_lost", return_value=True)
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "victory"


@pytest.mark.asyncio
async def test_turn_miss(battleship_client, mocker, turn_request):
    mocker.patch("battleship.utils.check_if_player_lost", return_value=False)
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["result"] == "miss"
