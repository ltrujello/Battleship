import logging
import os
from collections import defaultdict
from aiohttp import web
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec
from battleship.api.urls import urls
from battleship.models.database import BattleshipDatabase, DATABASE_URL
from battleship.schema import server_response_for_validation_error

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    LOGGER.info("Starting battleship server...")
    app = web.Application(
        middlewares=[validation_middleware]
    )
    app.add_routes(urls)
    app["battleship_db"] = BattleshipDatabase(DATABASE_URL)
    app["websockets"] = defaultdict(set)

    setup_aiohttp_apispec(
        app,
        url="/battleship/docs",
        error_callback=server_response_for_validation_error
    )

    web.run_app(app, host="0.0.0.0", port=8080)
