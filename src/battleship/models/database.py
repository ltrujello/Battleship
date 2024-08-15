import logging
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, update, or_
from battleship.models.player import Player
from battleship.models.game import Game
from battleship.models.ship import Ship
from battleship.models.guess import Guess

DB_USERNAME = "testuser"
DB_PASSWD = "testpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "foo"
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

LOGGER = logging.getLogger(__name__)


class BattleshipDatabase:
    def __init__(self, URL=None):
        if URL is None:
            URL = DATABASE_URL
        self.engine = create_async_engine(URL, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def add_game(self, game: Game):
        async with self.async_session() as session:
            session.add(game)
            await session.commit()
            await session.refresh(game)
        return game

    async def get_game(self, game_id: int):
        async with self.async_session() as session:
            result = await session.get(Game, game_id)
        return result

    async def update_game(self, game_id: int, updates: dict):
        async with self.async_session() as session:
            # Update the player with the provided updates
            await session.execute(
                update(Game).where(Game.id == game_id).values(**updates)
            )
            await session.commit()

    async def add_player(self, player: Player):
        async with self.async_session() as session:
            session.add(player)
            await session.commit()
            await session.refresh(player)
        return player

    async def add_ship(self, ship: Ship):
        async with self.async_session() as session:
            session.add(ship)
            await session.commit()
            await session.refresh(ship)
        return ship

    async def get_ship(self, ship_id: int):
        async with self.async_session() as session:
            result = await session.get(Ship, ship_id)
        return result

    async def update_ship(self, ship_id: int, updates: dict) -> Ship:
        async with self.async_session() as session:
            # Update the player with the provided updates
            result = await session.execute(
                update(Ship).where(Ship.id == ship_id).values(**updates).returning(Ship)
            )
            await session.commit()
            updated_ship = result.fetchone()[0]

        return updated_ship

    async def add_guess(self, guess: Guess):
        async with self.async_session() as session:
            session.add(guess)
            await session.commit()
            await session.refresh(guess)
        return guess

    async def get_player_ships(self, game_id: int, player_id: int) -> list[Ship]:
        async with self.async_session() as session:
            stmt = select(Ship).where(
                Ship.game_id == game_id, Ship.player_id == player_id
            )
            result = await session.execute(stmt)
            ships = result.scalars().all()
            return ships

    async def get_player_by_id(self, player_id: int):
        async with self.async_session() as session:
            result = await session.get(Player, player_id)
        return result

    async def get_player_games(self, player_id: int):
        async with self.async_session() as session:
            stmt = select(Game).where(
                or_(
                    Game.player_1_id == player_id,
                    Game.player_2_id == player_id,
                )
            )
            result = await session.execute(stmt)
            games = result.scalars().all()
        return games

    async def increment_ship_hits(self, ship_id: int) -> int:
        # Construct an update statement that increments the `hits` column atomically
        async with self.async_session() as session:
            stmt = (
                update(Ship)
                .where(Ship.id == ship_id)
                .values(hits=Ship.hits + 1)
                .returning(Ship.hits)
            )

            # Execute the statement and fetch the result
            result = await session.execute(stmt)
            await session.commit()

            # Optionally, return the new value of `hits` for the ship
            new_hits_value = result.fetchone()[0]
            return new_hits_value

    async def get_ship_hits(self, ship_ids: list[int]) -> list[Guess]:
        """
        Retrieves a list of guesses which successfully hit any of the ships
        in the given list of ship_ids.
        """
        async with self.async_session() as session:
            stmt = select(Guess).where(Guess.ship_id.in_(ship_ids))
            result = await session.execute(stmt)
            hits = result.scalars().all()
            return hits

    async def get_player_guesses(self, game_id: int, player_id) -> list[Guess]:
        """
        Retrieves a list of guesses a player has made so far in a game.
        """
        async with self.async_session() as session:
            stmt = select(Guess).where(
                Guess.game_id == game_id, Guess.player_id == player_id
            )
            result = await session.execute(stmt)
            ships = result.scalars().all()
            return ships

    async def get_game_details(self, game_id: int, player_id) -> list[Guess]:
        """
        Queries the database to construct game details for a player
        """
        async with self.async_session() as session:
            # Fetch the game
            game = await session.get(Game, game_id)
            if game is None:
                LOGGER.error(f"Failed to locate {game_id=} in database")
                return None
            enemy_player_id: int = (
                game.player_1_id if game.player_1_id != player_id else game.player_2_id
            )

            # Fetch player's ships
            stmt = select(Ship).where(
                Ship.game_id == game_id, Ship.player_id == player_id
            )
            result = await session.execute(stmt)
            player_ships = result.scalars().all()

            # Fetch player's guess history
            stmt = select(Guess).where(
                Guess.game_id == game_id, Guess.offense_player_id == player_id
            )
            result = await session.execute(stmt)
            player_guesses = result.scalars().all()

            # Fetch enemy's guess history
            stmt = select(Guess).where(
                Guess.game_id == game_id, Guess.offense_player_id == enemy_player_id
            )
            result = await session.execute(stmt)
            enemy_guesses = result.scalars().all()

        return {
            "game": game,
            "player_ships": player_ships,
            "player_guesses": player_guesses,
            "enemy_guesses": enemy_guesses,
        }
