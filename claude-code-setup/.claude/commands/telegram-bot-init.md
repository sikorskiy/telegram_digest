---
description: Инициализация нового Telegram бота
---

# Создание Telegram бота

Создай структуру для нового Telegram бота с библиотекой из $ARGUMENTS (aiogram/python-telegram-bot/telethon/telegraf)

## План:

### 1. Структура проекта
```
bot/
├── handlers/           # Обработчики команд и сообщений
│   ├── __init__.py
│   ├── start.py       # /start команда
│   ├── help.py        # /help команда
│   └── messages.py    # Обработка текстовых сообщений
├── keyboards/          # Клавиатуры (inline, reply)
│   ├── __init__.py
│   └── main.py
├── database/           # Работа с БД
│   ├── __init__.py
│   └── models.py      # SQLAlchemy models / MongoDB schemas
├── middleware/         # Middleware (логирование, аутентификация)
│   ├── __init__.py
│   └── auth.py
├── utils/              # Утилиты
│   ├── __init__.py
│   └── helpers.py
├── config.py           # Конфигурация
├── main.py             # Entry point
├── .env.example        # Пример переменных окружения
└── requirements.txt    # Зависимости
```

### 2. Основные файлы

#### main.py
- Инициализация бота
- Регистрация handlers
- Запуск polling/webhook

#### config.py
- Загрузка из .env
- Валидация обязательных параметров (BOT_TOKEN)

#### handlers/start.py
- Приветственное сообщение
- Регистрация пользователя в БД
- Главное меню

### 3. Базовая функциональность

Реализуй:
- [ ] /start - приветствие и регистрация
- [ ] /help - список доступных команд
- [ ] Обработка текстовых сообщений
- [ ] Логирование (в файл и консоль)
- [ ] Graceful shutdown
- [ ] Error handling (try-except с уведомлением админа)

### 4. .env файл
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
DATABASE_URL=sqlite:///bot.db
LOG_LEVEL=INFO
```

### 5. README.md
Создай README с:
- Описание бота
- Установка (pip install -r requirements.txt)
- Настройка (.env)
- Запуск (python main.py)
- Структура проекта

### 6. Best Practices
- Используй async/await
- Добавь typing hints
- Обрабатывай все возможные ошибки
- Логируй важные события
- Используй environment variables для секретов
- Добавь rate limiting для предотвращения спама

Создай полностью рабочий шаблон бота, готовый к расширению.
