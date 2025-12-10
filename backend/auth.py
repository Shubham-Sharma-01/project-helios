"""Authentication service."""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os

from backend.models import User
from backend.database import get_db

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def register_user(email: str, password: str, full_name: str = None) -> Tuple[bool, Optional[User], str]:
    """
    Register a new user.
    
    Returns:
        (success, user, message)
    """
    with get_db() as db:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return False, None, "User with this email already exists"
        
        # Create new user
        hashed_pw = hash_password(password)
        new_user = User(
            email=email,
            password_hash=hashed_pw,
            full_name=full_name
        )
        
        db.add(new_user)
        db.flush()  # Get the ID
        db.refresh(new_user)
        
        return True, new_user, "User registered successfully"


def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[User], str]:
    """
    Authenticate a user.
    
    Returns:
        (success, user, message)
    """
    with get_db() as db:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return False, None, "Invalid email or password"
        
        if not user.is_active:
            return False, None, "User account is disabled"
        
        if not verify_password(password, user.password_hash):
            return False, None, "Invalid email or password"
        
        return True, user, "Authentication successful"


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    with get_db() as db:
        return db.query(User).filter(User.id == user_id).first()


def get_user_by_token(token: str) -> Optional[User]:
    """Get user by JWT token."""
    user_id = verify_token(token)
    if not user_id:
        return None
    return get_user_by_id(user_id)

