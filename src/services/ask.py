# src/services/ask.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.chunk import ChunkRepository

class AskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chunk_repo = ChunkRepository(session)

    async def answer_question_on_video(self, video_id: str, question: str) -> str:
        # Step 1 & 2: We don't use embeddings yet, just fetch ALL chunks for the video
        video_uuid = uuid.UUID(video_id)
        
        # We pass 0 for timestamps to get the entire video context
        chunks = await self.chunk_repo.get_by_video_id(
            video_id=video_uuid, 
            from_timestamp=0, 
            to_timestamp=0
        )
        
        if not chunks:
            return "No transcript found for this video."

        # Step 3: Combine all text
        context_text = "\n".join([c.content for c in chunks])
        
        # Step 4: Send to your RAG/LLM chain
        # return await llm_chain.invoke(context=context_text, question=question)
        
        # Placeholder for now
        return f"Combining {len(chunks)} chunks from the database as context to answer: '{question}'"