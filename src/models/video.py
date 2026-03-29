import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
    
if TYPE_CHECKING:
    from src.models.chunk import Chunk


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

    # Establish a one-to-many relationship with the Chunk model
    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="video", cascade="all, delete-orphan")
    