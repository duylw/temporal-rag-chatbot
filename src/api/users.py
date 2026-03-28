from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db_session
from src.schemas.user import UserCreate, UserResponse
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.create_user(user_in)