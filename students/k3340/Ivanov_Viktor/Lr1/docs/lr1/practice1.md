# Практика 1.1 — In-memory API

**Стек:** FastAPI, Pydantic (без БД)

## Что реализовано

- CRUD для транзакций (`GET`, `POST`, `PUT`, `DELETE`)
- CRUD для категорий (`GET`, `POST`)
- Хранение данных в памяти (Python-списки)
- Валидация через Pydantic-модели

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `main.py` | FastAPI-приложение, роуты, in-memory списки |
| `models.py` | Pydantic-модели: `Transaction`, `Category`, `Tag`, `TransactionCreate`, `TransactionUpdate` |

## Модели

```python
class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class Transaction(BaseModel):
    id: int
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    category: Category
    tags: list[Tag] = []
    comment: Optional[str] = None
```

## Эндпоинты

```
GET    /transactions_list
GET    /transaction/{id}
POST   /transaction
PUT    /transaction/{id}
DELETE /transaction/delete/{id}

GET    /categories_list
GET    /category/{id}
POST   /category
```

## Особенности

- Данные сбрасываются при перезапуске сервера
- Нет пользователей и аутентификации
- Теги хранятся вложенно в объекте транзакции
