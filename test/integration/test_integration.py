import pytest


@pytest.fixture(scope="session")
def test_session():
    return {}


PLAYER_SHIPS = [
    {
        "size": 5,
        "orientation": "horizontal",
        "start_position_x": 4,
        "start_position_y": 0,
    },
    {
        "size": 4,
        "orientation": "vertical",
        "start_position_x": 0,
        "start_position_y": 4,
    },
    {
        "size": 4,
        "orientation": "horizontal",
        "start_position_x": 6,
        "start_position_y": 9,
    },
    {
        "size": 3,
        "orientation": "vertical",
        "start_position_x": 3,
        "start_position_y": 7,
    },
    {
        "size": 3,
        "orientation": "vertical",
        "start_position_x": 9,
        "start_position_y": 2,
    },
    {
        "size": 3,
        "orientation": "horizontal",
        "start_position_x": 5,
        "start_position_y": 7,
    },
    {
        "size": 2,
        "orientation": "horizontal",
        "start_position_x": 0,
        "start_position_y": 9,
    },
    {
        "size": 2,
        "orientation": "vertical",
        "start_position_x": 9,
        "start_position_y": 6,
    },
    {
        "size": 2,
        "orientation": "vertical",
        "start_position_x": 5,
        "start_position_y": 4,
    },
    {
        "size": 2,
        "orientation": "horizontal",
        "start_position_x": 0,
        "start_position_y": 2,
    },
]


@pytest.mark.asyncio
async def test_create_players(
    test_session, battleship_client, create_new_player_request
):
    # Create player 1
    ret = await battleship_client.post(
        "v1/battleship/player", json=create_new_player_request
    )
    assert ret.status == 200
    data = await ret.json()
    test_session["player_1_id"] = data["player_id"]

    # Create player 2
    ret = await battleship_client.post(
        "v1/battleship/player", json=create_new_player_request
    )
    assert ret.status == 200
    test_session["player_2_id"] = (await ret.json())["player_id"]


@pytest.mark.asyncio
async def test_create_new_game(test_session, battleship_client, new_game_request):
    # Create a game
    player_1_id = test_session["player_1_id"]
    player_2_id = test_session["player_2_id"]
    new_game_request = {
        "player_1_id": player_1_id,
        "player_2_id": player_2_id,
        "initial_player": player_1_id,
    }
    ret = await battleship_client.post("v1/battleship/game", json=new_game_request)
    assert ret.status == 200

    test_session["game_id"] = (await ret.json())["game_id"]


@pytest.mark.asyncio
async def test_create_player_ships(test_session, battleship_client):
    # Set up player_1 ships
    player_1_id = test_session["player_1_id"]
    game_id = test_session["game_id"]
    for ship in PLAYER_SHIPS:
        new_ship_request = {
            "player_id": player_1_id,
            "game_id": game_id,
            "ship": ship,
        }
        ret = await battleship_client.post(
            "/v1/battleship/game/player/create_new_ship", json=new_ship_request
        )
        assert ret.status == 200

    # Set up player_2 ships
    player_2_id = test_session["player_2_id"]
    for ship in PLAYER_SHIPS:
        new_ship_request = {
            "player_id": player_2_id,
            "game_id": game_id,
            "ship": ship,
        }
        ret = await battleship_client.post(
            "/v1/battleship/game/player/create_new_ship", json=new_ship_request
        )
        assert ret.status == 200


@pytest.mark.asyncio
async def test_place_ship_outside_board(test_session, battleship_client):
    # Set up player_1 ships
    player_1_id = test_session["player_1_id"]
    game_id = test_session["game_id"]
    new_ship_request = {
        "player_id": player_1_id,
        "game_id": game_id,
        "ship": {
            "size": 5,
            "orientation": "vertical",
            "start_position_x": 9,
            "start_position_y": 6,
        },
    }
    ret = await battleship_client.post(
        "/v1/battleship/game/player/create_new_ship", json=new_ship_request
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_place_ship_overlaps(test_session, battleship_client):
    # Set up player_1 ships
    player_1_id = test_session["player_1_id"]
    game_id = test_session["game_id"]
    new_ship_request = {
        "player_id": player_1_id,
        "game_id": game_id,
        "ship": {
            "size": 3,
            "orientation": "vertical",
            "start_position_x": 0,
            "start_position_y": 2,
        },
    }
    ret = await battleship_client.post(
        "/v1/battleship/game/player/create_new_ship", json=new_ship_request
    )
    assert ret.status == 400


@pytest.mark.asyncio
async def test_take_turn_hits(test_session, battleship_client):
    offense_player_id = test_session["player_1_id"]
    defense_player_id = test_session["player_2_id"]
    game_id = test_session["game_id"]
    take_turn_request = {
        "offense_player_id": offense_player_id,
        "defense_player_id": defense_player_id,
        "game_id": game_id,
        "guess_position_x": 0,
        "guess_position_y": 7,
    }
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=take_turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["current_player_id"] == defense_player_id
    assert data["result"] == "hit"


@pytest.mark.asyncio
async def test_take_turn_misses(test_session, battleship_client):
    offense_player_id = test_session["player_2_id"]
    defense_player_id = test_session["player_1_id"]
    game_id = test_session["game_id"]
    take_turn_request = {
        "offense_player_id": offense_player_id,
        "defense_player_id": defense_player_id,
        "game_id": game_id,
        "guess_position_x": 0,
        "guess_position_y": 8,
    }
    ret = await battleship_client.post(
        "/v1/battleship/game/player/take_turn", json=take_turn_request
    )
    assert ret.status == 200
    data = await ret.json()
    assert data["current_player_id"] == defense_player_id
    assert data["result"] == "miss"


@pytest.mark.asyncio
async def test_get_player_games(test_session, battleship_client):
    player_id = test_session["player_1_id"]
    params = {"player_id": player_id}
    ret = await battleship_client.get("/v1/battleship/player/games", params=params)
    assert ret.status == 200
    data = await ret.json()
    assert len(data) > 0
