from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import List, Optional

from starlette.responses import HTMLResponse

# Конфигурация
SECRET_KEY = "your_secret_key"  # Секретный ключ для подписи JWT
ALGORITHM = "HS256"  # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время действия токена в минутах

# Инициализация приложения FastAPI
app = FastAPI()

# Модели данных
class User(BaseModel):
    username: str
    level: str  # Уровень кэшбека
    cashback: float  # Процент кэшбека

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


# Имитация базы данных пользователей
fake_users_db = {
    "employee": {
        "username": "employee",
        "full_name": "Evgeniia",
        "hashed_password": "fakehashedpassword",
        "level": "gold",
        "cashback": 5.0
    },
    "client": {
        "username": "client",
        "full_name": "Appletree",
        "hashed_password": "fakehashedpassword123",
        "level": "silver",
        "cashback": 3.0
    }
}

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функция для проверки пароля
def fake_hash_password(password: str):
    return "fakehashed" + password

# Функция для получения пользователя из базы данных
def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)

# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return fake_hash_password(plain_password) == hashed_password

# Функция для создания токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Стартовая страница</title>
        </head>
        <body>
            <h1>Добро пожаловать в FastAPI!</h1>
            <p>Это ваша стартовая страница.</p>
        </body>
    </html>
    """

# Эндпоинт для получения токена
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинт для получения информации о бонусах
@app.get("/bonuses/", response_model=User )
async def read_bonuses(current_user: User = Depends(get_current_user)):
    return current_user  # Возвращаем информацию о пользователе

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
