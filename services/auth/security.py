import hashlib
import os
import secrets


def generate_salt() -> str:
    """Generate a random 16-byte hex salt."""
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    """Hash a password using PBKDF2 HMAC SHA-256 with salt."""
    if not password or not salt:
        return ""
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex()


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """Verify that password matches stored hash."""
    if not password or not salt or not stored_hash:
        return False
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, stored_hash)
