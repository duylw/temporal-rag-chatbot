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