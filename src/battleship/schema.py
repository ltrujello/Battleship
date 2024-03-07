import logging
import json
from aiohttp import web
from typing import Optional, Mapping
from marshmallow import Schema, fields
from marshmallow.fields import Integer, String, Nested, ValidationError
from enum import Enum

LOGGER = logging.getLogger(__name__)


class ShipOrientation(Enum):
    horizontal = "horizontal"
    vertical = "vertical"


class GameStatus(Enum):
    in_progress = "in_progress"
    complete = "complete"


class GuessResult(Enum):
    hit = "hit"
    miss = "miss"
    victory = "victory"


class Ship(Schema):
    size = Integer(required=True)
    orientation = String(
        required=True,
        validate=fields.validate.OneOf([e.value for e in ShipOrientation]),
    )
    start_position_x = Integer(required=True)
    start_position_y = Integer(required=True)


class CreateNewGameRequest(Schema):
    player_1_id = Integer(required=True)
    player_2_id = Integer(required=True)
    initial_player = Integer(required=True)


class AddNewShipRequest(Schema):
    player_id = Integer(required=True)
    game_id = Integer(required=True)
    ship = Nested(Ship)


class TakeTurnRequest(Schema):
    offense_player_id = Integer(required=True)
    defense_player_id = Integer(required=True)
    game_id = Integer(required=True)
    guess_position_x = Integer(required=True)
    guess_position_y = Integer(required=True)


class TakeTurnResponse(Schema):
    current_player_id = Integer(required=True)
    status = String(
        required=True, validate=fields.validate.OneOf([e.value for e in GameStatus])
    )


def server_response_for_validation_error(
    error: ValidationError,
    req: web.Request,
    schema: Schema,
    error_status_code: Optional[int] = None,
    error_headers: Optional[Mapping[str, str]] = None,
) -> None:
    LOGGER.error(f"Experienced a validation error: {error.messages=}")
    raise web.HTTPBadRequest(
        text=json.dumps(error.messages),
        headers=error_headers,
        content_type="application/json",
    )
