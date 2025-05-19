# Budget Tracker API

![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-green)
![Docker](https://img.shields.io/badge/Docker-supported-blue)

RESTful API для управления бюджетом с JWT-аутентификацией, построенное на FastAPI.

## ✨ Особенности
- Аутентификация через JWT
- Управление бюджетом (создание, просмотр и обновление доходов и расходов)
- Интерактивная документация API
- Контейнеризация через Docker

## 🛠 Технологический стек
- **Python 3.9** - основа приложения
- **FastAPI** - высокопроизводительный веб-фреймворк
- **JWT** - безопасная аутентификация
- **Docker** - контейнеризация
- **OpenAPI 3.0** - спецификация API

## 📋 Требования
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Быстрый старт

1. Клонируйте репозиторий:
git clone <ваш-репозиторий>

2. Запустите приложение:
docker-compose up --build

3. Сервисы будут доступны:
- **Auth Service**: `http://localhost:8000`
- **Budget Service**: `http://localhost:8001`

## 📡 Основные эндпоинты

### 🔐 Auth Service (`http://localhost:8000`)

#### Информация о пользователе
GET /auth/users/me
Authorization: Bearer <ваш_токен>

### 📝 Budget Service (`http://localhost:8001`)
#### Создание дохода
POST /incomes/
Authorization: Bearer <ваш_токен>
Content-Type: application/json

{
  "title": "Премия",
  "description": "Работник месяца",
  "value": "20000",
  "periodicity": "once",
  "due_date": "2024-06-25"
}

**Поля:**
| Поле          | Тип     | Обязательное | Значения                   |
|---------------|---------|--------------|----------------------------|
| title         | string  | ✓            | max 100 символов          |
| description   | string  | ✓            | -                         |
| value         | integer | ✓            | сумма дохода               |
| due_date      | date    |              | YYYY-MM-DD                |
| periodicity   | string  |              | "once", "daily", "weekly", "monthly"   |
| periodicity_value | integer  |       | день недели или месяца |
| assignee_id   | integer |              | ID пользователя           |

#### Список доходов
GET /incomes/
Authorization: Bearer <ваш_токен>

#### Создание расхода
POST /costs/
Authorization: Bearer <ваш_токен>
Content-Type: application/json

{
  "title": "Подарок",
  "description": "Подарок на день рождение другу",
  "value": "10000",
  "periodicity": "once",
  "due_date": "2024-06-05"
}

**Поля:**
| Поле          | Тип     | Обязательное | Значения                   |
|---------------|---------|--------------|----------------------------|
| title         | string  | ✓            | max 100 символов          |
| description   | string  | ✓            | -                         |
| value         | integer | ✓            | сумма расхода               |
| due_date      | date    |              | YYYY-MM-DD                |
| periodicity   | string  |              | "once", "daily", "weekly", "monthly"   |
| periodicity_value | integer  |       | день недели или месяца |
| assignee_id   | integer |              | ID пользователя           |

#### Список расходов
GET /costs/
Authorization: Bearer <ваш_токен>

## 🔑 Данные мастер-пользователя
- **Логин**: `admin`
- **Пароль**: `secret`

Спецификация OpenAPI: `openapi.yml`


## ⚙️ Технические детали
- JWT-аутентификация с Bearer токенами
- Поддержка методов GET/POST/PUT
- Валидация через Pydantic
- Хранение данных в памяти
- Запуск через Docker Compose

## 🏗 Архитектура
Два микросервиса:
1. **Auth Service**: управление пользователями и токенами
2. **Budget Service**: CRUD операции с бюджетом

Схема: `workspace.dsl` (Structurizr DSL)

## 📜 Коды ответов
| Код | Описание              |
|-----|-----------------------|
| 200 | Успешно               |
| 201 | Создано               |
| 400 | Неверный запрос       |
| 401 | Не авторизован        |
| 403 | Доступ запрещен       |
| 404 | Не найдено            |
| 422 | Ошибка валидации      |
