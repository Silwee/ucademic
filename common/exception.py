from fastapi import HTTPException, status

user_existed_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already existed",
)

login_failed_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)