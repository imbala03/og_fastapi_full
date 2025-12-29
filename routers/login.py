from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from database import get_db
from models.user import User
from schemas.user import LoginRequest, UserOut
from utils.hash import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        identifier = payload.identifier.strip()
        password = payload.password

        # Try Email or Phone (case-insensitive for email)
        if "@" in identifier:
            # Case-insensitive email matching
            user = db.query(User).filter(
                func.lower(User.email) == func.lower(identifier)
            ).first()
        else:
            user = db.query(User).filter(User.phone == identifier).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Check if password hash exists
        if not user.password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User password not set in database"
            )

        # Verify bcrypt password
        try:
            password_valid = verify_password(password, user.password)
        except Exception as e:
            # If password verification fails due to hash format issues
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password verification error: {str(e)}"
            )
        
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Update last_login timestamp
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        return user
    except HTTPException:
        # Re-raise HTTP exceptions (like Invalid credentials)
        raise
    except Exception as e:
        # Catch any other exceptions and return a proper error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
