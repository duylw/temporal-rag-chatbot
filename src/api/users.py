from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    user = await service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    return user

@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 10,
    offset: int = 0
):
    service = UserService(db)
    return await service.list_users(limit=limit, offset=offset)