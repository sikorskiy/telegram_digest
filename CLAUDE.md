# Telegram Digest - Контекст проекта для Claude Code

## Цель проекта

Создание автоматического дайджеста постов из Telegram-каналов в форматах PDF и EPUB с AI-саммари на русском языке. CLI-приложение для локального запуска и GitHub Actions.

## Архитектура

### Основные компоненты

1. **Fetcher** (`src/fetcher.py`) - Асинхронная загрузка постов через Telethon
   - SQLite session storage для авторизации
   - Поддержка множественных каналов из YAML
   - Идемпотентность по msg_id и SHA-256

2. **Summarizer** (`src/summarizer.py`) - Генерация русских саммари через OpenAI gpt-4o
   - Ограничение: ≤40 слов (1-2 предложения)
   - Кэширование результатов в Firebase

3. **HTML Converter** (`src/html_converter.py`) - Сохранение форматирования Telegram
   - Bold, italic, code, links, emojis
   - Корректная обработка переносов строк

4. **PDF Builder** (`src/pdf_digest.py`) - WeasyPrint для генерации PDF
   - Jinja2 шаблоны с CSS
   - Сохранение кликабельных ссылок

5. **EPUB Builder** - ebooklib для создания электронных книг
   - Оглавление по каналам
   - Мобильная читабельность

6. **Database** (`src/firebase_db.py`) - Firebase Firestore
   - Коллекции: posts, runs
   - Синхронизация между локальным и CI/CD

7. **CLI** (`src/cli.py`) - Typer интерфейс

## Ключевые файлы

- `src/fetcher.py:TelegramFetcher` - Основной класс для загрузки постов
- `src/summarizer.py:OpenAISummarizer` - Генерация саммари
- `src/html_converter.py:convert_telegram_html()` - Конвертация форматирования
- `src/pdf_digest.py:build_pdf()` - Генерация PDF
- `src/firebase_db.py:FirebaseDB` - Работа с БД
- `channels.yaml` - Список каналов для мониторинга
- `.env` - Секреты (TELEGRAM_API_ID, OPENAI_API_KEY, Firebase credentials)

## Команды CLI

```bash
# Загрузить посты за последние N дней
telegram-digest fetch --channels channels.yaml --days 1

# Сгенерировать PDF за конкретную дату
telegram-digest build-pdf --date 2025-06-08

# Сгенерировать EPUB
telegram-digest build-epub --date 2025-06-08

# Полный пайплайн (fetch + summarize + build)
telegram-digest run
```

## Технический стек

- **Python 3.11+** с Poetry для управления зависимостями
- **Telethon** - async Telegram API
- **OpenAI API** - gpt-4o для саммари
- **WeasyPrint** - HTML→PDF с CSS
- **ebooklib** - генерация EPUB
- **Firebase Firestore** - облачная БД
- **Typer** - CLI framework
- **GitHub Actions** - CI/CD с cron и артефактами

## Важные детали

### Форматирование Telegram
- **Критично**: сохранять bold, italic, links, emojis из оригинала
- Используется `html_converter.py` для парсинга Telegram entities
- WeasyPrint поддерживает CSS для стилизации

### Кэширование и идемпотентность
- Проверка дубликатов по `msg_id` и SHA-256 текста
- Firebase хранит обработанные посты
- Избегаем повторных вызовов OpenAI API

### Firebase конфигурация
- Credentials в `.env`: `GOOGLE_APPLICATION_CREDENTIALS=path/to/serviceAccountKey.json`
- В CI/CD: через GitHub Secrets
- Коллекции: `posts` (данные), `runs` (метаданные запусков)

### OpenAI промпты
```
SYSTEM: Ты опытный российский редактор, конспектируешь телеграм-посты.
USER: Текст: «{plain_text}»
Сформулируй выжимку 1-2 предложениями (≤40 слов).
```

## Workflow разработки

1. **Локальная разработка**:
   - Использовать `.env` для секретов
   - Тестировать на 1-2 каналах с `--days 1`
   - Проверять PDF локально перед коммитом

2. **GitHub Actions**:
   - Workflow в `.github/workflows/`
   - Секреты настроены через Settings > Secrets
   - Артефакты PDF/EPUB хранятся 90 дней
   - Cron schedule для автоматического запуска

3. **Тестирование**:
   - Проверять сохранение форматирования (bold/italic/links)
   - Валидировать PDF в разных ридерах
   - EPUB тестировать в Calibre/Apple Books

## Дорожная карта

### v0.2 (следующая версия)
- [ ] Обложка для PDF/EPUB
- [ ] Оглавление с разбивкой по каналам
- [ ] Улучшенные стили и читабельность

### v0.3
- [ ] Обработка групповых чатов
- [ ] Weekly summary из чатов

### v0.4
- [ ] Веб-UI (FastAPI + HTMX)
- [ ] Настройка каналов через интерфейс

### v0.5
- [ ] Отправка в Telegram бот / email
- [ ] Push уведомления

### v0.6
- [ ] RAG для тематической фильтрации
- [ ] Тегирование и ключевые инсайты

## Стиль кода

- **Форматирование**: используй black и isort
- **Типы**: указывай type hints где возможно
- **Async**: все операции с Telegram через async/await
- **Ошибки**: обрабатывай network timeouts, API rate limits
- **Логирование**: используй logging для отладки

## Частые проблемы

1. **"No session found"** → запустить аутентификацию Telethon
2. **"Firebase auth failed"** → проверить `.env` и `GOOGLE_APPLICATION_CREDENTIALS`
3. **"Rate limit exceeded"** → добавить exponential backoff в fetcher
4. **PDF не генерируется** → проверить WeasyPrint dependencies (Cairo, Pango)
5. **Эмодзи не отображаются** → установить шрифты с emoji поддержкой

## Безопасность

- **НИКОГДА** не коммитить `.env` файлы
- Firebase credentials только через secrets
- Telegram session файлы в `.gitignore`
- API ключи только через environment variables

## Полезные ссылки

- Telethon Docs: https://docs.telethon.dev/
- OpenAI API: https://platform.openai.com/docs
- WeasyPrint: https://doc.courtbouillon.org/weasyprint/
- Firebase Python SDK: https://firebase.google.com/docs/firestore/quickstart

## Примечания для Claude Code

- При работе с форматированием Telegram всегда проверяй `html_converter.py`
- Тестируй генерацию PDF на малых датасетах перед полным прогоном
- Используй `--days 1` для быстрой итерации
- Проверяй Firebase квоты при работе с большими объемами
