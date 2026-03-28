from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db_session

router = APIRouter()

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db_session)):
    # Your repository layer will use this db session!
    return {"message": "Database connected"}