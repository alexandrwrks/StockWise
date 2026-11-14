from argon2 import PasswordHasher

ph = PasswordHasher()

class PasswordSecurity:
    def hash_password(self, password: str) -> str:
        return ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return ph.verify(hashed_password, password)

password_security = PasswordSecurity()