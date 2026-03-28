from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate
from src.models.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user(self, user_in: UserCreate) -> User:
        # Business logic goes here (e.g., checking for duplicates)
        return await self.repository.create(user_in)

    async def get_user(self, user_id: int) -> User:
        # Implement logic to retrieve a user by ID
        return await self.repository.get_by_id(user_id)
    
    async def list_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        # Implement logic to list users with pagination
        return await self.repository.list(limit=limit, offset=offset)