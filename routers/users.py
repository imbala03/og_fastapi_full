from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User, UserRole
from schemas.user import UserCreate, UserOut, UserPasswordResponse
from utils.hash import hash_password
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    """List all users (for debugging)"""
    return db.query(User).all()


@router.get("/exclude-poweradmin", response_model=List[UserOut])
def list_users_exclude_poweradmin(db: Session = Depends(get_db)):
    """
    Return all users except those with the role "poweradmin".
    """
    users = db.query(User).filter(User.role != UserRole.poweradmin).all()
    return users


@router.get("/role/{role}", response_model=List[UserOut])
def list_users_by_role(role: str, db: Session = Depends(get_db)):
    """
    Return all users filtered by role.
    """
    # Normalize and validate role against enum
    role_value = role.strip().lower()
    valid_roles = {r.value for r in UserRole}
    if role_value not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed: {', '.join(sorted(valid_roles))}"
        )

    # Compare directly against the enum value (no LOWER() casting on DB enum)
    users = db.query(User).filter(User.role == role_value).all()
    return users


@router.get("/password-hash", response_model=UserPasswordResponse)
def get_user_password_hash(
    user_id: Optional[int] = Query(None, description="User ID"),
    username: Optional[str] = Query(None, description="Username (name)"),
    email: Optional[str] = Query(None, description="User email"),
    db: Session = Depends(get_db)
):
    """
    Get the password hash for a user by user_id, username, or email.
    
    NOTE: Passwords are hashed using bcrypt and CANNOT be decrypted.
    This endpoint returns the stored hash, not the original password.
    """
    if not user_id and not username and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one parameter (user_id, username, or email) must be provided"
        )
    
    # Build query based on provided parameters
    query = db.query(User)
    
    if user_id:
        query = query.filter(User.id == user_id)
    elif username:
        query = query.filter(func.lower(User.name) == func.lower(username.strip()))
    elif email:
        query = query.filter(func.lower(User.email) == func.lower(email.strip()))
    
    user = query.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPasswordResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=user.password
    )


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Validate that at least email or phone is provided
        if not payload.email and not payload.phone:
            raise HTTPException(
                status_code=400, 
                detail="Either email or phone must be provided"
            )
        
        # Check existing email/phone (case-insensitive for email)
        if payload.email:
            existing_user = db.query(User).filter(
                func.lower(User.email) == func.lower(payload.email)
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already used")

        if payload.phone:
            existing_user = db.query(User).filter(User.phone == payload.phone).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Phone already used")

        hashed = hash_password(payload.password)

        new_user = User(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            password=hashed,   # IMPORTANT!
            role=payload.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )
