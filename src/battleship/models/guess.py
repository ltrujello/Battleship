from battleship.models.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum, Integer
import enum


class GuessResult(str, enum.Enum):
    hit = "hit"
    miss = "miss"
    victory = "victory"


class Guess(Base):
    __tablename__ = "guess"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    position_x: Mapped[int] = mapped_column(Integer)
    position_y: Mapped[int] = mapped_column(Integer)
    result: Mapped[GuessResult] = mapped_column(Enum(GuessResult))

    game = relationship("Game")
    player = relationship("Player")

    def __repr__(self) -> str:
        return f"Guess(id={self.id!r}, game_id={self.game_id!r}, player_id={self.player_id!r}, position_x={self.position_x!r}, position_y={self.position_y!r}, result={self.result!r})"
