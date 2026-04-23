# Авторизация и JWT

Аутентификация реализована **вручную** — без `fastapi-users` или других библиотек.

## Хэширование паролей

Используется `pbkdf2_hmac` (Python stdlib) с случайной солью:

```python
PASSWORD_SCHEME = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 120_000

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{PASSWORD_SCHEME}${PBKDF2_ITERATIONS}${salt.hex()}${password_hash.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    scheme, iterations, salt_hex, expected_hash_hex = hashed_password.split("$", maxsplit=3)
    calculated = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
    )
    return hmac.compare_digest(calculated.hex(), expected_hash_hex)
```

## JWT-токены

Генерация и проверка через `PyJWT`:

```python
def create_access_token(subject: str, expires_minutes: int = None) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError:
        return None
```

## Dependency: get_current_user

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_access_token(token)
    user = session.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

## Демонстрация через Swagger UI

1. `POST /api/v1/auth/register` — зарегистрировать пользователя
2. `POST /api/v1/auth/login` — получить `access_token`
3. Нажать кнопку **Authorize** в Swagger UI
4. Вставить токен в поле **OAuth2PasswordBearer** (только токен, без слова Bearer)
5. Все защищённые эндпоинты теперь доступны
