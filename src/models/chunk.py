import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from src.models.video import Video

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    content: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(Integer)
    duration: Mapped[int] = mapped_column(Integer)

    # Foreign key constraint linking to the Video table
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    
    # Establish the many-to-one relationship with the Video model
    video: Mapped["Video"] = relationship("Video", back_populates="chunks")