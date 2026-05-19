from datetime import datetime, timedelta

from jose import jwt, JWTError

from passlib.context import CryptContext

from fastapi import HTTPException, status


SECRET_KEY = "burst_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
def hash_password(password):
    password = str(password).strip()
    return pwd_context.hash(password[:72])


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
    plain_password[:72],
    hashed_password
)
    

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
def create_reset_token(
    email: str
):

    expire = (
        datetime.utcnow()

        + timedelta(
            minutes=15
        )
    )

    to_encode = {

        "sub":
        email,

        "exp":
        expire,

        "type":
        "reset"
    }

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=
        ALGORITHM
    )

    return encoded_jwt