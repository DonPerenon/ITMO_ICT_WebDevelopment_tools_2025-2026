# Модели данных

## Таблицы (SQLModel)

| Таблица | Описание |
|---------|---------|
| `User` | Пользователи системы |
| `Category` | Категории транзакций (доход/расход) |
| `Tag` | Теги для транзакций |
| `Transaction` | Финансовые операции |
| `TransactionTagLink` | Связь многие-ко-многим: транзакция ↔ тег |
| `Budget` | Бюджеты по категориям за период |
| `Goal` | Финансовые цели |

## Схема связей

```
User ──┬──< Category ──< Transaction ──< TransactionTagLink >── Tag
       ├──< Tag
       ├──< Transaction
       ├──< Budget
       └──< Goal
```

- **one-to-many**: `User → Category`, `User → Tag`, `User → Transaction`, `User → Budget`, `User → Goal`
- **many-to-many**: `Transaction ↔ Tag` через `TransactionTagLink`

## Ассоциативная сущность TransactionTagLink

```python
class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(foreign_key="transaction.id", primary_key=True)
    tag_id: Optional[int] = Field(foreign_key="tag.id", primary_key=True)
    relevance: int = Field(default=1, ge=1, le=5)  # доп. поле
    note: Optional[str] = None                      # доп. поле
```

## User

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Goal (новая в practice3)

```python
class GoalStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: Optional[date] = None
    status: GoalStatus = Field(default=GoalStatus.active)
    user_id: int = Field(foreign_key="user.id")
```
