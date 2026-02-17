from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import decode_access_token
from app.crud import user as crud_user
from app.models.user import User
from typing import Optional

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    print(f"🔍 Validating token: {token[:20]}...")
    payload = decode_access_token(token)
    if payload is None:
        print(f"❌ TOKEN INVALID: decode returned None")
        raise credentials_exception
    
    user_id: Optional[int] = payload.get("sub")
    print(f"   Payload sub (user_id): {user_id}")
    if user_id is None:
        print(f"❌ TOKEN INVALID: no 'sub' in payload")
        raise credentials_exception
    
    # Get user from database
    try:
        user = await crud_user.get(db, id=int(user_id))
        if user is None:
            print(f"❌ AUTH FAILED: User ID {user_id} not found in DB")
            raise credentials_exception
        print(f"✅ AUTH SUCCESS: User {user.email} authenticated")
        return user
    except Exception as e:
        print(f"❌ AUTH DB ERROR: {str(e)}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
