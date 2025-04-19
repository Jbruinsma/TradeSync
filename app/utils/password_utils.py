import bcrypt
from typing import Tuple

def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    Returns the hashed password as bytes.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed

def verify_password(password: str, hashed: bytes) -> bool:
    """
    Verify a password against its hash.
    Returns True if the password matches, False otherwise.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Check if password matches hash
    return bcrypt.checkpw(password_bytes, hashed)

def generate_salt() -> bytes:
    """
    Generate a new salt for password hashing.
    Returns the salt as bytes.
    """
    return bcrypt.gensalt() 