import logging
from aiohttp import web
from battleship.urls import urls

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))

def battleship_database():
    pass

if __name__ == "__main__":
    LOGGER.info("Starting battleship server...")
    app = web.Application(
        middlewares=[validation_middleware]
    )
    app.add_routes(urls)

    web.run_app(app, host="0.0.0.0", port=8080)
