---
description: Быстрое создание утилитарного скрипта
---

# Создание быстрого скрипта

Создай готовый к использованию скрипт для: $ARGUMENTS

## Требования к скрипту:

### 1. Структура
```python
#!/usr/bin/env python3
"""
Описание скрипта
"""
import argparse
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('input', help='...')
    parser.add_argument('--output', '-o', help='...')
    args = parser.parse_args()

    # Логика

if __name__ == '__main__':
    main()
```

### 2. Обязательные элементы
- [ ] Shebang (#!/usr/bin/env python3)
- [ ] Docstring с описанием
- [ ] Argparse для параметров
- [ ] Логирование (logging)
- [ ] Error handling (try/except)
- [ ] Help message (--help работает)
- [ ] Проверка входных данных

### 3. Типичные паттерны

**Работа с файлами:**
```python
def process_file(input_path, output_path):
    try:
        with open(input_path, 'r') as f:
            data = f.read()

        # Обработка
        result = transform(data)

        with open(output_path, 'w') as f:
            f.write(result)

        logger.info(f"Обработано: {input_path} → {output_path}")
    except FileNotFoundError:
        logger.error(f"Файл не найден: {input_path}")
        sys.exit(1)
```

**Работа с API:**
```python
import requests

def fetch_data(api_url, token):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Ошибка API: {e}")
        return None
```

**Batch обработка:**
```python
from pathlib import Path

def process_directory(dir_path, pattern='*.txt'):
    files = Path(dir_path).glob(pattern)
    for file in files:
        logger.info(f"Обработка: {file}")
        process_file(file)
```

**Cron-friendly (для автоматизации):**
```python
# Добавить в crontab:
# 0 9 * * * /usr/bin/python3 /path/to/script.py

def is_running_in_cron():
    return not sys.stdin.isatty()

def main():
    if is_running_in_cron():
        # Отправить результат в Telegram/email
        notify_results()
```

### 4. Полезные библиотеки

**Для CLI:**
- `typer` - современный CLI (лучше argparse)
- `click` - популярная альтернатива
- `rich` - красивый вывод в терминал

**Для работы с данными:**
- `pandas` - CSV/Excel обработка
- `requests` - HTTP запросы
- `beautifulsoup4` - парсинг HTML

**Для автоматизации:**
- `schedule` - cron на Python
- `python-dotenv` - env переменные
- `pathlib` - работа с путями (встроенная)

### 5. Сделай скрипт production-ready:
- Добавь `requirements.txt`
- Создай `.env.example` если нужны секреты
- Напиши README с примерами использования
- Добавь `chmod +x script.py` в инструкцию
- Протестируй edge cases

Создай полностью рабочий скрипт, который можно сразу использовать.
