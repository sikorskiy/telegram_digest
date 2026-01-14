---
description: Изучение структуры проекта или модуля
---

# Исследование кодовой базы

Изучи структуру проекта/модуля: $ARGUMENTS

## План исследования:

### 1. Обзор структуры
- Покажи дерево директорий (основные папки)
- Определи тип проекта (web app, library, CLI tool, etc.)
- Найди entry points (main.py, index.js, cmd/main.go)

### 2. Архитектура
- Какой архитектурный паттерн используется?
  - MVC, Clean Architecture, Microservices, Monolith
- Как организованы слои?
  - Presentation / Business Logic / Data Access
- Зависимости между модулями

### 3. Ключевые компоненты
Для каждого модуля опиши:
- Назначение (что делает)
- Основные классы/функции
- Зависимости (что использует)
- Входные/выходные данные

### 4. Data Flow
Проследи путь данных:
```
User Request → API Gateway → Service → Database → Response
```

### 5. Configuration & Setup
- Как настраивается проект?
- Какие env переменные нужны?
- Внешние зависимости (DB, APIs, services)

### 6. Testing
- Где тесты?
- Тестовое покрытие (если видно)
- Как запустить тесты?

### 7. Build & Deployment
- Как собирается проект?
- Docker? CI/CD?
- Production dependencies

## Формат ответа:

```markdown
# Обзор проекта [Название]

## Тип: [Web API / CLI / Library / Desktop App]

## Структура:
src/
  ├── core/       - Бизнес-логика
  ├── api/        - HTTP handlers
  ├── db/         - Database access
  └── utils/      - Утилиты

## Технологии:
- Framework: Express.js
- Database: PostgreSQL
- Auth: JWT

## Entry points:
- src/index.js - HTTP сервер
- src/cli.js - CLI интерфейс

## Основные модули:

### 1. Authentication (src/auth/)
Отвечает за авторизацию пользователей через JWT токены.
- login() - проверяет credentials
- verifyToken() - валидирует токены
- refreshToken() - обновляет токены

### 2. Payment Processing (src/payments/)
Интеграция с платёжными системами (Stripe, PayPal).
- processPayment() - обрабатывает платежи
- handleWebhook() - принимает уведомления

## Data Flow:
1. User отправляет POST /api/login
2. AuthController.login() проверяет пароль
3. Если ok → генерирует JWT
4. JWT отправляется клиенту
5. Клиент добавляет JWT в заголовки
6. Middleware verifyToken() проверяет на каждом запросе

## Setup:
```bash
npm install
cp .env.example .env
# Настрой DATABASE_URL
npm run migrate
npm run dev
```

## Notes:
- Код хорошо организован, следует MVC
- Тесты есть, покрытие ~60%
- TODO: добавить rate limiting
```

## Если изучаешь конкретную фичу:
1. Найди где реализована (grep/search)
2. Прочитай основной код
3. Найди где вызывается
4. Проследи flow от начала до конца
5. Проверь тесты (они часто показывают примеры использования)

Будь конкретен. Избегай общих фраз типа "это модуль для работы с данными".
