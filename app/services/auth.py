from sqlalchemy import select
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone

from app.core.config import settings

from app.models.refresh_token import RefreshToken

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    generate_refresh_token,
    hash_refresh_token,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    statement = select(User).where(
        User.email == email
    )

    return db.scalar(statement)


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:

    statement = select(User).where(
        User.username == username
    )

    return db.scalar(statement)


def create_user(
    db: Session,
    user_data: RegisterRequest,
) -> User:

    hashed_password = hash_password(
        user_data.password
    )

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_user_access_token(
    user: User,
) -> str:

    return create_access_token(
        str(user.id)
    )
    

def create_refresh_token(
    db: Session,
    user: User,
) -> str:

    raw_token = generate_refresh_token()

    token_hash = hash_refresh_token(
        raw_token
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.refresh_token_expire_days
        )
    )

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(refresh_token)
    db.commit()

    return raw_token


def get_refresh_token(
    db: Session,
    raw_token: str,
) -> RefreshToken | None:

    token_hash = hash_refresh_token(
        raw_token
    )

    statement = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash
    )

    return db.scalar(statement)


def validate_refresh_token(
    refresh_token: RefreshToken,
) -> bool:

    now = datetime.now(timezone.utc)

    if refresh_token.revoked_at is not None:
        return False

    if refresh_token.expires_at <= now:
        return False

    return True


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
) -> None:

    refresh_token.revoked_at = datetime.now(
        timezone.utc
    )

    db.commit()