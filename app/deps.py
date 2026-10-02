from typing import Optional

from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.database import get_db
from app.models import User
from app.schemas import TokenData

oauth2_scheme=OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False,
)

async def get_or_create_default_user(db:AsyncSession)->User:
    result=await db.scalars(
        select(User).where(User.username=="demo_user")
    )
    user=result.first()

    if not user:
        user=User(
            username="demo_user",
            email="demo@example.com",
            hashed_password=get_password_hash("DemoPass123!"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user

async def get_current_user(
    token:Optional[str]=Depends(oauth2_scheme),
    db:AsyncSession=Depends(get_db),
)->User:
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )

    if not token:
        if settings.REQUIRE_AUTH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Bearer token required.",
                headers={"WWW-Authenticate":"Bearer"},
            )

        return await get_or_create_default_user(db)

    try:
        payload=jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        username:Optional[str]=payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data=TokenData(username=username)

    except JWTError:
        raise credentials_exception

    result=await db.scalars(
        select(User).where(User.username==token_data.username)
    )
    user=result.first()

    if user is None:
        raise credentials_exception

    return user

async def get_optional_user(
    token:Optional[str]=Depends(oauth2_scheme),
    db:AsyncSession=Depends(get_db),
)->Optional[User]:
    if not token:
        return None

    try:
        payload=jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        username:Optional[str]=payload.get("sub")

        if username is None:
            return None

    except JWTError:
        return None

    result=await db.scalars(
        select(User).where(User.username==username)
    )

    return result.first()