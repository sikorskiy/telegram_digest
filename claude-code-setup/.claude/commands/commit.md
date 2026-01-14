---
description: Создать коммит с автоматическим сообщением
---

# Умный git commit

Проанализируй изменения и создай осмысленный коммит.

## Процесс:

### 1. Анализ изменений
```bash
git status
git diff --staged
```

### 2. Классификация типа изменений
Определи тип по Conventional Commits:
- `feat`: новая фича
- `fix`: исправление бага
- `refactor`: рефакторинг без изменения функциональности
- `docs`: обновление документации
- `style`: форматирование, пробелы (без изменения логики)
- `test`: добавление/изменение тестов
- `chore`: обновление зависимостей, конфигурации
- `perf`: оптимизация производительности

### 3. Генерация сообщения
Формат:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Примеры хороших коммитов:**
```
feat(auth): add JWT token refresh mechanism

Implemented automatic token refresh when access token expires.
Added RefreshTokenMiddleware and refresh endpoint.

Closes #123
```

```
fix(api): handle null response in user fetch

Added null check before accessing user.id to prevent
NullPointerException when user not found.
```

```
refactor(database): extract query builders into separate module

Moved all query building logic from controllers to
database/queries.py for better separation of concerns.
```

### 4. Создание коммита

**Если изменения небольшие:**
```bash
git add .
git commit -m "type(scope): краткое описание"
```

**Если изменения значительные:**
```bash
git add .
git commit -m "type(scope): краткое описание

Подробное объяснение что и зачем изменено.
Может быть несколько параграфов.

Closes #123"
```

## Правила хорошего коммита:

✅ **DO:**
- Используй императивное наклонение: "add", не "added" или "adds"
- Первая строка ≤50 символов
- Тело коммита ≤72 символа на строку
- Объясняй **почему**, не **что** (что видно из diff)
- Разделяй несвязанные изменения на отдельные коммиты

❌ **DON'T:**
- "fix stuff" - неинформативно
- "WIP" - не коммить незавершённое
- Смешивать несвязанные изменения
- Коммитить закомментированный код
- Коммитить console.log / print для дебага

## Автоматическая проверка:

Перед коммитом проверь:
1. [ ] Код скомпилирован / запускается
2. [ ] Тесты проходят
3. [ ] Нет закомментированного кода
4. [ ] Нет debug логов (console.log, print)
5. [ ] Нет конфликтов
6. [ ] .gitignore настроен (нет .env, credentials)

Проанализируй текущие изменения и предложи осмысленное сообщение коммита.
