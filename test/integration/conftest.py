import pytest
import asyncio
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec
from aiohttp import web
from battleship.api.urls import urls

from battleship.schema import server_response_for_validation_error
from battleship.models.database import BattleshipDatabase
from battleship.models.base import Base

# docker run --name my-test-postgres -e POSTGRES_DB=foo -e POSTGRES_USER=testuser -e POSTGRES_PASSWORD=testpassword -p 5432:5432 -d postgres
DB_USERNAME = "testuser"
DB_PASSWD = "testpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "foo"
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


async def setup_db(battleship_db):
    async with battleship_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def battleship_database(event_loop):
    battleship_db = BattleshipDatabase(DATABASE_URL)
    event_loop.run_until_complete(setup_db(battleship_db))
    return battleship_db


@pytest.fixture
def battleship_client(event_loop, battleship_database, aiohttp_client):
    app = web.Application(middlewares=[validation_middleware])
    app["battleship_db"] = battleship_database
    app.add_routes(urls)
    setup_aiohttp_apispec(app, error_callback=server_response_for_validation_error)
    return event_loop.run_until_complete(aiohttp_client(app))


#     # event_loop.run_until_complete(setup_db(battleship_db))
