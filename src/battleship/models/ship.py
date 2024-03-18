from battleship.models.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, Enum
import enum


class ShipOrientation(str, enum.Enum):
    horizontal = "horizontal"
    vertical = "vertical"


class Ship(Base):
    __tablename__ = "ship"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    orientation: Mapped[ShipOrientation] = mapped_column(Enum(ShipOrientation))
    start_position_x: Mapped[int] = mapped_column(Integer)
    start_position_y: Mapped[int] = mapped_column(Integer)
    size: Mapped[int] = mapped_column(Integer)
    hits: Mapped[int] = mapped_column(Integer)

    game = relationship("Game")
    player = relationship("Player")

    def __repr__(self) -> str:
        return f"Ship(id={self.id!r}, game_id={self.game_id!r}, player_id={self.player_id!r}, orientation={self.orientation!r}, start_position_x={self.start_position_x!r}, start_position_y={self.start_position_y!r}, size={self.size!r}, hits={self.hits!r})"
