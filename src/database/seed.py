import csv
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.video import Video
from src.models.chunk import Chunk

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

async def seed_data_if_empty(session: AsyncSession):
    # Check if there's any data already
    result = await session.execute(select(Video).limit(1))
    if result.scalars().first() is not None:
        # Data already exists, skip seeding
        return

    # 1. Load Videos
    videos = {} # Store by video_uuid to look up later
    with open(os.path.join(DATA_DIR, "videos.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid_id = uuid.UUID(row["video_uuid"])
            video = Video(
                id=vid_id,
                name=row["video_name"],
                url=row["video_url"]
            )
            session.add(video)
            videos[vid_id] = video

    # 2. Load Chunks
    chunks = {} # Store by chunk_uuid
    with open(os.path.join(DATA_DIR, "chunks.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chunk_id = uuid.UUID(row["chunk_uuid"])
            
            try:
                timestamp = int(float(row["timestamp"])) if row["timestamp"] else 0
            except ValueError:
                timestamp = 0
                
            try:
                duration = int(float(row["duration"])) if row["duration"] else 0
            except ValueError:
                duration = 0

            chunk = Chunk(
                id=chunk_id,
                content=row["content"],
                timestamp=timestamp,
                duration=duration
                # video_id will be mapped next
            )
            chunks[chunk_id] = chunk

    # 3. Map video_id to chunks using video_chunks.csv
    with open(os.path.join(DATA_DIR, "video_chunks.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid_id = uuid.UUID(row["video_uuid"])
            chunk_id = uuid.UUID(row["chunk_uuid"])
            if chunk_id in chunks:
                chunks[chunk_id].video_id = vid_id
                session.add(chunks[chunk_id])

    await session.commit()
    print("Database seeded successfully with CSV data.")
