from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, Token
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    refresh_access_token
)

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)


@router.post(
    '/register',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary='Register a new user'
)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    user = await register_user(db, user_in)
    return user


@router.post(
    '/login',
    response_model=Token,
    summary='Obtain access token via username & password'
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token = create_access_token(
        data={'sub': str(user.id)},
        expires_delta=timedelta(minutes=15)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    '/refresh',
    response_model=Token,
    summary='Refresh expired access token'
)
async def refresh_token(
        token: str,
        db: AsyncSession = Depends(get_db)
):
    new_token = await refresh_access_token(db, token)
    return {'access_token': new_token, 'token_type': 'bearer'}