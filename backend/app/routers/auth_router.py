from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.db.models import User
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user."""
    
    # Check email domain
    allowed_domains = ['pvpsit.ac.in', 'pvpsiddhartha.ac.in']
    email_domain = user_data.email.split('@')[-1]
    if email_domain not in allowed_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only @pvpsit.ac.in and @pvpsiddhartha.ac.in email addresses are allowed",
        )
    
    # Check if username or email already exists
    result = await session.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Create new user
    # Auto-grant admin privileges to @pvpsiddhartha.ac.in domain users
    is_admin = user_data.email.endswith('@pvpsiddhartha.ac.in')
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pw,
        is_admin=is_admin,
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    user_response = UserResponse.model_validate(new_user)
    
    return Token(access_token=access_token, user=user_response)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Login user and return access token."""
    
    # Find user by email
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    user_response = UserResponse.model_validate(user)
    
    return Token(access_token=access_token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get current user information."""
    
    result = await session.execute(
        select(User).where(User.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)
