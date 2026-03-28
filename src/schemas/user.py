from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool

    # Allows Pydantic to read data even if it is not a dict (like a SQLAlchemy model)
    model_config = {"from_attributes": True}