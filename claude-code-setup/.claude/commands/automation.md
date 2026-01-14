---
description: Настройка автоматизации рутинных задач
---

# Автоматизация рутинных задач

Настрой автоматизацию для: $ARGUMENTS

## Типы автоматизации:

### 1. Cron Jobs (Linux/Mac)
Регулярное выполнение задач по расписанию.

**Примеры:**
```bash
# Открыть crontab
crontab -e

# Каждый день в 9:00 утра
0 9 * * * /usr/bin/python3 /path/to/morning_routine.py

# Каждый час
0 * * * * /path/to/check_something.sh

# Каждый понедельник в 10:00
0 10 * * 1 /path/to/weekly_report.py

# Каждые 5 минут
*/5 * * * * /path/to/monitor.py
```

**Best Practices:**
- Используй абсолютные пути
- Логируй результаты: `>> /var/log/myscript.log 2>&1`
- Проверяй что скрипт работает вручную перед добавлением в cron
- Используй flock для предотвращения параллельных запусков

### 2. GitHub Actions (CI/CD)
Автоматизация в репозитории.

**Примеры:**
```yaml
# .github/workflows/daily-tasks.yml
name: Daily Tasks
on:
  schedule:
    - cron: '0 9 * * *'  # Каждый день в 9:00 UTC
  workflow_dispatch:  # Ручной запуск

jobs:
  run-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Python script
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: python scripts/daily_task.py
```

**Use Cases:**
- Backup данных
- Парсинг и агрегация данных
- Генерация отчётов
- Обновление статических сайтов
- Мониторинг сайтов/API

### 3. Python Schedule
Автоматизация внутри Python приложения.

```python
import schedule
import time

def morning_routine():
    """Выполняется каждое утро в 9:00"""
    print("Доброе утро! Вот твои задачи на день:")
    # ... логика

def check_emails():
    """Проверка каждые 10 минут"""
    # ... логика

# Регистрация задач
schedule.every().day.at("09:00").do(morning_routine)
schedule.every(10).minutes.do(check_emails)
schedule.every().monday.at("10:00").do(weekly_report)

# Запуск
while True:
    schedule.run_pending()
    time.sleep(1)
```

### 4. Telegram бот + автоматические сообщения
Отправка уведомлений/отчётов в Telegram.

```python
import asyncio
from telegram import Bot

async def send_daily_report():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    chat_id = os.getenv('MY_CHAT_ID')

    # Собираем данные
    report = generate_report()

    # Отправляем
    await bot.send_message(chat_id=chat_id, text=report)

# Запускать из cron или schedule
```

### 5. n8n / Zapier Webhooks
Интеграция с no-code платформами.

```python
import requests

def trigger_n8n_workflow(data):
    """Триггерит n8n workflow через webhook"""
    webhook_url = "https://your-n8n.app/webhook/xyz"
    requests.post(webhook_url, json=data)

# Использование
trigger_n8n_workflow({
    "event": "task_completed",
    "task_id": 123,
    "timestamp": datetime.now().isoformat()
})
```

## Популярные сценарии автоматизации:

### Утренняя рутина
```python
def morning_routine():
    # 1. Погода на сегодня
    weather = get_weather()

    # 2. Задачи на день
    tasks = get_today_tasks()

    # 3. Важные email'ы
    emails = check_important_emails()

    # 4. Новости
    news = get_news_digest()

    # 5. Отправить всё в Telegram
    send_to_telegram(f"""
    🌅 Доброе утро!

    🌤 Погода: {weather}

    📋 Задачи:
    {tasks}

    📧 Важные письма: {len(emails)}

    📰 Новости:
    {news}
    """)
```

### Вечерний обзор
```python
def evening_review():
    # 1. Что сделано
    completed = get_completed_tasks()

    # 2. Прогресс по целям
    progress = calculate_progress()

    # 3. Статистика
    stats = get_daily_stats()

    # 4. Планирование завтра
    tomorrow_plan = generate_tomorrow_plan()

    send_to_telegram(f"""
    🌙 Вечерний обзор

    ✅ Выполнено: {len(completed)} задач
    📊 Прогресс: {progress}%
    ⏱ Время работы: {stats['work_hours']}ч

    📅 Завтра:
    {tomorrow_plan}
    """)
```

### Мониторинг изменений
```python
def monitor_website_changes():
    """Проверяет изменения на сайте каждые 5 минут"""
    url = "https://example.com/page"
    previous_hash = load_hash()

    content = requests.get(url).text
    current_hash = hashlib.md5(content.encode()).hexdigest()

    if current_hash != previous_hash:
        notify("🔔 Сайт обновился!", url)
        save_hash(current_hash)
```

### Backup автоматизация
```python
def daily_backup():
    """Ежедневный бэкап важных файлов"""
    import shutil
    from datetime import datetime

    source = "/path/to/important/data"
    backup_dir = f"/backups/{datetime.now().strftime('%Y-%m-%d')}"

    shutil.copytree(source, backup_dir)

    # Удалить старые бэкапы (>30 дней)
    cleanup_old_backups(days=30)

    # Отправить в облако
    upload_to_cloud(backup_dir)
```

## Setup checklist:

1. [ ] Определи что нужно автоматизировать
2. [ ] Выбери метод (cron/GitHub Actions/schedule)
3. [ ] Создай скрипт
4. [ ] Протестируй вручную
5. [ ] Добавь логирование
6. [ ] Настрой уведомления об ошибках
7. [ ] Задокументируй в README
8. [ ] Настрой расписание
9. [ ] Мониторь первую неделю

Какую задачу хочешь автоматизировать? Опиши и я помогу реализовать.
