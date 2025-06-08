# Telegram Digest Agent

Версия: 2025‑06‑08

## 1. Цели проекта

Собрать посты избранных Telegram‑каналов (и позже чатов) за заданный период → превратить их в читабельный PDF/EPUB‑дайджест, где:
- перед каждым постом стоит краткое (1‑2 предложения) summary на русском;
- сохранено оригинальное форматирование Telegram (жирный/курсив, эмодзи, ссылки);
- каждая ссылка внутри поста обрабатывается интеллектуально:
  - если в ссылке содержится значимый текст (статья, пост, форма, сообщение, канал) — создаётся дайджест/описание;
  - если нет — ссылка отображается «как есть» без лишних затрат токенов.

Ограничения MVP: CLI‑приложение, без веб‑интерфейса, без платных БД/хостинга (OpenAI API оплачивается). Работает локально и/или на GitHub Actions.

## 2. Функциональные требования MVP

| # | Функция | Описание |
|---|---------|----------|
| F‑01 | Загрузка постов | По расписанию (cron) получать все посты из списка каналов за period_days. |
| F‑02 | Кэш & idempotency | Не обрабатывать один и тот же post/link дважды (по msg_id, url, SHA-256 текста). |
| F‑03 | Summary постов | Для каждого поста формировать выжимку ≤ 2 предложений (OpenAI ChatCompletion, gpt‑4o). |
| F‑04 | Интеллект‑обработка ссылок | 1. Определить тип ссылки (канал, пост, статья, форма, «просто сайт»).<br>2. Если ссылка содержит релевантный текст → дайджест; иначе — пропустить.<br>3. Для Telegram‑линков: извлечь пост/канал‑title и коротко описать. |
| F‑05 | PDF генерация | Сохранить оригинальное форматирование + summary + дайджесты ссылок. |
| F‑06 | Хранение данных | Локальная SQLite: таблицы posts, links, runs. |
| F‑07 | Автономность | Приложение работает офлайн (кроме API вызовов). |
| F‑08 | GitHub Actions CD | Возможность запускать на free‑runner'e, хранить state через Actions Cache. |

## 3. Технический стек

| Слой | Библиотека / сервис | Почему |
|------|---------------------|---------|
| Telegram API | Telethon | async, rich entities, SQLite session‑storage |
| Link scraping | readability-lxml, requests, beautifulsoup4 | Чистый текст без рекламы |
| LLM summaries | OpenAI gpt‑3.5‑turbo (классификатор) + gpt‑4o (финальный summary) | Баланс цена/качество |
| PDF | WeasyPrint (HTML→PDF) | CSS, эмодзи, гиперссылки |
| CLI | Typer | Авто‑help, nice UX |
| Env / Config | python‑dotenv, YAML для каналов | Простота |
| DB | SQLite + sqlite‑utils | Zero‑setup, файловая, совместима с GitHub Actions Cache |
| CI/CD | GitHub Actions + actions/cache + upload-artifact | Бесплатно, cron, артефакты PDF |

## 4. Архитектура Pipeline

```
┌───────── Scheduler (cron / GA) ─────────┐
│                                         │
│ 1. fetcher.py ──► 2. summarizer.py ──► 3. pdf_builder.py │
│    (Telethon)       (OpenAI)              (WeasyPrint)  │
│                                         │
└───────► storage/telegram-digest.db & output/*.pdf ◄─────┘
```

## 5. Стратегия persistence

### 5.1 Локальная установка
- storage/telegram-digest.db и storage/session.session хранятся на диске.
- Cron запускает poetry run telegram-digest fetch --days 1.

### 5.2 GitHub Actions
- Restore cache: качаем последнюю БД по ключу digest-db-*.
- Запускаем пайплайн → обновляем БД, кладём PDF в output/.
- Save cache: сохраняем файл как digest-db-${{github.run_id}}.
- PDF публикуется через upload-artifact, доступно 90 дней.

## 6. План разработки (Milestones)

| MS | Содержание | Оценка |
|----|------------|---------|
| 0 | Бутстрап — репо, Poetry, каркас, CI, .env | 0.5‑1 д |
| 1 | Fetcher — загрузка постов, заполнение posts | 1 д |
| 2 | Summaries — генерация выжимок (post) + кеш | 1 д |
| 3 | Link Handler — классификация & дайджест URL | 1.5 д |
| 4 | PDF Builder — Jinja2 template → WeasyPrint | 1 д |
| 5 | CI/CD — cron‑workflow, cache, artefacts | 0.5 д |

Всего ≈ 5‑6 чистых дней.

## 7. Доступные команды CLI (прототип)

```bash
telegram-digest fetch   --channels config/channels.yml --days 1
telegram-digest build-pdf --date 2025-06-08
telegram-digest run     # fetch + summarize + pdf в один клик
```

## 8. Prompt шаблоны

### 8.1 Summary Post

```
SYSTEM: Ты опытный российский редактор, конспектируешь телеграм‑посты.
USER: Текст: «{plain_text}»
Сформулируй выжимку 1‑2 предложениями (⩽ 40 слов).
```

### 8.2 Link Classifier

```
USER: Ниже текст страницы/поста. Ответь «RELEVANT» если материал содержит новую полезную информацию по теме канала «{channel_theme}», иначе «SKIP».

<CONTENT>
```

### 8.3 Link Digest

```
SYSTEM: Ты писал короткие обзорные заметки.
USER: Создай краткое описание (1 абзац) сути по тексту: «{article}»
```

## 9. Дорожная карта улучшений
- v0.2 EPUB‑экспорт (ebooklib), обложка, оглавление.
- v0.3 Обработка групповых чатов → weekly summary.
- v0.4 Веб‑UI (FastAPI + HTMX) для настройки каналов, скачивания выпусков.
- v0.5 Push готового файла в Telegram боту / e‑mail.
- v0.6 Тематическая фильтрация (RAG), тегирование, ключевые инсайты.

## 10. Чек‑лист готовности MVP
- [ ] Репозиторий и CI настроены
- [ ] Fetcher тянет посты
- [ ] Summary постов генерируются и кешируются
- [ ] Ссылки классифицируются и дайджестятся
- [ ] PDF формируется корректно (локально и в GA)
- [ ] Документация README.md описывает установку и запуск 