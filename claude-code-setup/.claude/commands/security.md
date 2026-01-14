---
description: Security audit кода
---

# Security Audit

Проведи аудит безопасности для: $ARGUMENTS

## Проверь на уязвимости:

### 1. Injection атаки
- **SQL Injection**: параметризованные запросы? ORM правильно используется?
- **NoSQL Injection**: валидация в MongoDB/Firestore запросах?
- **Command Injection**: shell_exec, system, eval с пользовательским вводом?
- **XSS**: экранирование HTML в шаблонах? Content Security Policy?
- **Path Traversal**: проверка `../` в путях к файлам?

### 2. Authentication & Authorization
- Проверка прав доступа на каждом эндпоинте?
- JWT токены проверяются и валидируются?
- Сессии безопасно управляются?
- Возможен ли обход авторизации?

### 3. Sensitive Data Exposure
- Пароли хэшируются (bcrypt, argon2)?
- Секреты в .env, не в коде?
- Логи не содержат пароли/токены?
- HTTPS для передачи данных?
- Чувствительные данные зашифрованы в БД?

### 4. Input Validation
- Все входные данные валидируются?
- Type checking (особенно в динамических языках)?
- Длина строк ограничена?
- Whitelist > Blacklist для валидации

### 5. Security Misconfiguration
- Дефолтные пароли изменены?
- Debug mode выключен в продакшене?
- Ошибки не показывают стек трейсы пользователям?
- CORS настроен правильно?

### 6. Rate Limiting & DoS
- Rate limiting на API эндпоинтах?
- Защита от brute force (логин)?
- Timeout на долгие операции?
- Размер загружаемых файлов ограничен?

### 7. Dependencies
- Известные уязвимости в зависимостях?
- Запусти: `npm audit` / `pip-audit` / `cargo audit`

### 8. Business Logic
- Можно ли обойти payment flow?
- IDOR (Insecure Direct Object Reference)?
- Race conditions в критических операциях?

## Для каждой найденной проблемы дай:
1. **Описание риска** (severity: low/medium/high/critical)
2. **Пример эксплуатации** (как атакующий может использовать)
3. **Исправление** (конкретный код)
4. **Приоритет** (что фиксить в первую очередь)

Фокусируйся на реальных рисках, не на теоретических.
