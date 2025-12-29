import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Use bcrypt directly to avoid passlib compatibility issues
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    Uses bcrypt directly for better compatibility.
    """
    if not hashed or not plain:
        return False
    
    # Strip any whitespace from the hash
    hashed = hashed.strip()
    
    # Check if the hash is a valid bcrypt hash (starts with $2b$, $2a$, or $2y$)
    if hashed.startswith(('$2a$', '$2b$', '$2y$')):
        try:
            # Use bcrypt directly instead of passlib to avoid compatibility issues
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            # If bcrypt fails, try passlib as fallback
            try:
                return pwd_context.verify(plain, hashed)
            except Exception:
                return False
    
    # If it's not a bcrypt hash, it might be stored as plain text (legacy)
    # For security, we should migrate these, but for now allow comparison
    # WARNING: This is insecure and should be removed after migration
    if hashed == plain:
        return True
    
    return False
