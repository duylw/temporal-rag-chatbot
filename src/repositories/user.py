from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_in: UserCreate) -> User:
        user = User(email=user_in.email, name=user_in.name)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user