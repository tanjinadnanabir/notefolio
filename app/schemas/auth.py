from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    full_name: str | None = Field(
        default=None,
        max_length=100,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID # for str, error occurs
    email: EmailStr
    username: str
    full_name: str | None
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(
        from_attributes=True,
    )