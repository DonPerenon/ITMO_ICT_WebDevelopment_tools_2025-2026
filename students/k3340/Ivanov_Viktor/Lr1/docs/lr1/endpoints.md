# Эндпоинты

Базовый префикс: `/api/v1`

## Auth

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| POST | `/auth/register` | Регистрация нового пользователя | — |
| POST | `/auth/login` | Получение JWT-токена | — |

## Users

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/users/me` | Текущий пользователь | Bearer |
| GET | `/users` | Список пользователей | Bearer |
| PATCH | `/users/me` | Обновление профиля | Bearer |
| POST | `/users/me/change-password` | Смена пароля | Bearer |

## Categories

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/categories` | Список категорий | Bearer |
| GET | `/categories/{id}` | Одна категория | Bearer |
| POST | `/categories` | Создать категорию | Bearer |
| PATCH | `/categories/{id}` | Обновить категорию | Bearer |
| DELETE | `/categories/{id}` | Удалить категорию | Bearer |

## Tags

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/tags` | Список тегов | Bearer |
| GET | `/tags/{id}` | Один тег | Bearer |
| POST | `/tags` | Создать тег | Bearer |
| PATCH | `/tags/{id}` | Обновить тег | Bearer |
| DELETE | `/tags/{id}` | Удалить тег | Bearer |

## Transactions

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/transactions` | Список транзакций | Bearer |
| GET | `/transactions/{id}` | Одна транзакция | Bearer |
| POST | `/transactions` | Создать транзакцию | Bearer |
| PATCH | `/transactions/{id}` | Обновить транзакцию | Bearer |
| DELETE | `/transactions/{id}` | Удалить транзакцию | Bearer |

## Budgets

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/budgets` | Список бюджетов | Bearer |
| GET | `/budgets/{id}` | Один бюджет | Bearer |
| POST | `/budgets` | Создать бюджет | Bearer |
| PATCH | `/budgets/{id}` | Обновить бюджет | Bearer |
| DELETE | `/budgets/{id}` | Удалить бюджет | Bearer |
| GET | `/budgets/over-limit/list` | Бюджеты с превышением лимита | Bearer |

## Goals

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/goals` | Список целей | Bearer |
| GET | `/goals/{id}` | Одна цель | Bearer |
| POST | `/goals` | Создать цель | Bearer |
| PATCH | `/goals/{id}` | Обновить цель | Bearer |
| DELETE | `/goals/{id}` | Удалить цель | Bearer |

## Reports

| Метод | URL | Описание | Auth |
|-------|-----|---------|------|
| GET | `/reports/summary` | Финансовый отчёт (доходы/расходы/баланс/группировка) | Bearer |

Параметры `summary`: `date_from` и `date_to` (опционально).
