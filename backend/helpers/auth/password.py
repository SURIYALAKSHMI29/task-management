from passlib.context import CryptContext

context = CryptContext(schemes=["argon2"], deprecated="auto")


# Password hashing
def hash_password(password: str) -> str:
    return context.hash(password)


def verify_password(password, hashed_password) -> bool:
    return context.verify(password, hashed_password)
