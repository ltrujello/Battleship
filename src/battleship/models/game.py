import enum
from battleship.models.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum


class GameStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_1_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    player_2_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    current_player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus))

    player_1 = relationship("Player", foreign_keys=[player_1_id])
    player_2 = relationship("Player", foreign_keys=[player_2_id])
    current_player = relationship("Player", foreign_keys=[current_player_id])

    def __repr__(self) -> str:
        return f"Game(id={self.id!r}, player_1_id={self.player_1_id!r}, player_2_id={self.player_2_id!r}, current_player_id={self.current_player_id!r}, status={self.status!r})"
