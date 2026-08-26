from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
)
from app.services.auth import (
    authenticate_user,
    create_refresh_token,
    create_user,
    create_user_access_token,
    get_refresh_token,
    get_user_by_email,
    get_user_by_username,
    revoke_refresh_token,
    validate_refresh_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_email = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    existing_username = get_user_by_username(
        db,
        user_data.username,
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken.",
        )

    return create_user(
        db,
        user_data,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        login_data.email,
        login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_user_access_token(
        user
    )

    refresh_token = create_refresh_token(
        db,
        user,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    
    
@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    refresh_token = get_refresh_token(
        db,
        token_data.refresh_token,
    )

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if not validate_refresh_token(
        refresh_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is expired or revoked.",
        )

    user = refresh_token.user

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    revoke_refresh_token(
        db,
        refresh_token,
    )

    new_access_token = create_user_access_token(
        user
    )

    new_refresh_token = create_refresh_token(
        db,
        user,
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
    
    
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    refresh_token = get_refresh_token(
        db,
        token_data.refresh_token,
    )

    if refresh_token is not None:
        revoke_refresh_token(
            db,
            refresh_token,
        )

    return None


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user