import hashlib
import hmac


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, hashed_token: str) -> bool:
    return hmac.compare_digest(hashed_token, hash_token(token))
