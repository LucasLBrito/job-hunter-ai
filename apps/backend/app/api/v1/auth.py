from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.database import get_db
from app.schemas.auth import Token, SignupRequest
from app.schemas.user import UserResponse
from app.crud import user as crud_user
from app.core.security import create_access_token
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (min 8 characters)
    - **full_name**: Optional full name
    """
    print(f"\n{'='*60}")
    print(f"📝 SIGNUP ATTEMPT:")
    print(f"   Email: {user_in.email}")
    print(f"   Username: {user_in.username}")
    print(f"   Full Name: {user_in.full_name}")
    print(f"{'='*60}\n")
    
    # Check if email already exists
    existing_user = await crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        print(f"❌ SIGNUP FAILED: Email '{user_in.email}' already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_user = await crud_user.get_by_username(db, username=user_in.username)
    if existing_user:
        print(f"❌ SIGNUP FAILED: Username '{user_in.username}' already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        full_name=user_in.full_name
    )
    user = await crud_user.create(db, user_in=user_create)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    print(f"\n{'='*60}")
    print(f"🔐 LOGIN ATTEMPT:")
    print(f"   Username/Email: {form_data.username}")
    print(f"   Password length: {len(form_data.password)}")
    print(f"{'='*60}\n")
    
    """
    OAuth2 compatible token login
    
    - **username**: Email or username
    - **password**: User password
    
    Returns JWT access token
    """
    # Authenticate user
    user = await crud_user.authenticate(
        db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        print(f"❌ LOGIN FAILED: Invalid credentials for '{form_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    
    Requires authentication token
    """
    return current_user


@router.post("/test-token", response_model=UserResponse)
async def test_token(current_user: User = Depends(get_current_active_user)):
    """
    Test access token validity
    
    Returns current user if token is valid
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    
    Requires authentication token
    """
    updated_user = await crud_user.update(db, db_obj=current_user, obj_in=user_update)
    return updated_user

