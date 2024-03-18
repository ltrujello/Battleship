from battleship.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]

    def __repr__(self) -> str:
        return f"Player(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r}, email={self.email!r})"
