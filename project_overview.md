# Telegram Digest Agent

Версия: 2025‑06‑08

## 1. Цели проекта

Собрать посты избранных Telegram‑каналов за заданный период → превратить их в читабельный PDF + EPUB‑дайджест, где:
- перед каждым постом стоит краткое (1 предложение) summary на русском;
- сохранено оригинальное форматирование Telegram (жирный/курсив, эмодзи, ссылки, переносы строк);

Ограничения MVP: CLI‑приложение, без веб‑интерфейса. Работает локально и/или на GitHub Actions.

## 2. Функциональные требования MVP

| # | Функция | Описание |
|---|---------|----------|
| F‑01 | Загрузка постов | По расписанию (cron) получать все посты из списка каналов за period_days. |
| F‑02 | Кэш & idempotency | Не обрабатывать один и тот же post дважды (по msg_id, SHA-256 текста). |
| F‑03 | Summary постов | Для каждого поста формировать выжимку ≤ 1 предложений (OpenAI ChatCompletion, gpt‑4o). |
| F‑04 | PDF генерация | Сохранить оригинальное форматирование + summary. |
| F‑05 | EPUB генерация | Создать EPUB версию дайджеста с сохранением форматирования. |
| F‑06 | Хранение данных | Google Firebase: коллекции posts, runs. |
| F‑07 | Автономность | Приложение работает офлайн (кроме API вызовов). |
| F‑08 | GitHub Actions CD | Возможность запускать на free‑runner'e, хранить state через Actions Cache. |

## 3. Технический стек

| Слой | Библиотека / сервис | Почему |
|------|---------------------|---------|
| Telegram API | Telethon | async, rich entities, SQLite session‑storage |
| LLM summaries | OpenAI gpt‑4o | Качественные summary постов |
| PDF | WeasyPrint (HTML→PDF) | CSS, эмодзи, гиперссылки |
| EPUB | ebooklib | Создание EPUB файлов |
| CLI | Typer | Авто‑help, nice UX |
| Env / Config | python‑dotenv, YAML для каналов | Простота |
| DB | Google Firebase Firestore | Облачная БД, синхронизация между устройствами |
| CI/CD | GitHub Actions + actions/cache + upload-artifact | Бесплатно, cron, артефакты PDF/EPUB |

## 4. Архитектура Pipeline

```
┌───────── Scheduler (cron / GA) ─────────┐
│                                         │
│ 1. fetcher.py ──► 2. summarizer.py ──► 3. pdf_builder.py ──► 4. epub_builder.py │
│    (Telethon)       (OpenAI)              (WeasyPrint)         (ebooklib)      │
│                                         │
└───────► Firebase & output/*.pdf, *.epub ◄─────────────────────────────────────┘
```

## 5. Стратегия persistence

### 5.1 Локальная установка
- Firebase credentials хранятся в .env файле.
- Cron запускает python telegram-digest fetch --days 1.

### 5.2 GitHub Actions
- Firebase credentials передаются через GitHub Secrets.
- Запускаем пайплайн → обновляем Firebase, кладём PDF/EPUB в output/.
- PDF/EPUB публикуется через upload-artifact, доступно 90 дней.

## 6. План разработки (Milestones)

| MS | Содержание | Оценка |
|----|------------|---------|
| 0 | Бутстрап — репо, каркас, CI, .env | 0.5‑1 д |
| 1 | Fetcher — загрузка постов, заполнение Firebase | 1 д |
| 2 | Summaries — генерация выжимок (post) + кеш | 1 д |
| 3 | PDF Builder — Jinja2 template → WeasyPrint | 1 д |
| 4 | EPUB Builder — создание EPUB файлов | 1 д |
| 5 | CI/CD — cron‑workflow, artefacts | 0.5 д |

Всего ≈ 4.5‑5.5 чистых дней.

## 7. Доступные команды CLI (прототип)

```bash
telegram-digest fetch   --channels config/channels.yml --days 1
telegram-digest build-pdf --date 2025-06-08
telegram-digest build-epub --date 2025-06-08
telegram-digest run     # fetch + summarize + pdf + epub в один клик
```

## 8. Prompt шаблоны

### 8.1 Summary Post

```
SYSTEM: Ты опытный российский редактор, конспектируешь телеграм‑посты.
USER: Текст: «{plain_text}»
Сформулируй выжимку 1‑2 предложениями (⩽ 40 слов).
```

## 9. Дорожная карта улучшений
- v0.2 Обложка, оглавление для PDF/EPUB.
- v0.3 Обработка групповых чатов → weekly summary.
- v0.4 Веб‑UI (FastAPI + HTMX) для настройки каналов, скачивания выпусков.
- v0.5 Push готового файла в Telegram боту / e‑mail.
- v0.6 Тематическая фильтрация (RAG), тегирование, ключевые инсайты.

## 10. Чек‑лист готовности MVP
- [ ] Репозиторий и CI настроены
- [ ] Fetcher тянет посты
- [ ] Summary постов генерируются и кешируются
- [ ] PDF формируется корректно (локально и в GA)
- [ ] EPUB формируется корректно (локально и в GA)
- [ ] Firebase интеграция настроена
- [ ] Документация project_overview.md описывает установку и запуск 