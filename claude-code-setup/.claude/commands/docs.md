---
description: Генерация/обновление документации
---

# Документация

Создай или обнови документацию для: $ARGUMENTS

## Что документировать:

### 1. Code-level документация
- **Docstrings** (Python) / **JSDoc** (JavaScript) / **GoDoc** (Go):
  ```python
  def process_payment(amount: float, user_id: str) -> PaymentResult:
      """
      Обрабатывает платёж для пользователя.

      Args:
          amount: Сумма платежа в рублях (должна быть > 0)
          user_id: UUID пользователя

      Returns:
          PaymentResult с status и transaction_id

      Raises:
          ValueError: если amount <= 0
          PaymentError: если платёж не прошёл

      Example:
          >>> result = process_payment(100.0, "user-123")
          >>> print(result.status)
          'success'
      """
  ```

### 2. README файлы
Обнови README.md с секциями:
- **Что это**: краткое описание в 1-2 предложениях
- **Зачем**: какую проблему решает
- **Установка**: шаги для setup
- **Использование**: примеры кода
- **Конфигурация**: переменные окружения, настройки
- **API**: основные методы/эндпоинты
- **Разработка**: как контрибьютить
- **FAQ**: частые вопросы

### 3. API документация
Для публичных API:
- Эндпоинты и методы
- Параметры (обязательные/опциональные)
- Примеры запросов/ответов
- Коды ошибок
- Rate limits
- Authentication

### 4. Architecture документы
Для сложных модулей:
- Диаграммы (ASCII или Mermaid)
- Data flow
- Архитектурные решения (ADR)
- Trade-offs

### 5. Примеры использования
```javascript
// Базовый пример
const client = new ApiClient({ apiKey: 'xxx' })
const result = await client.fetchData()

// Продвинутый пример с error handling
try {
  const result = await client.fetchData({
    filters: { status: 'active' },
    limit: 100
  })
  console.log(result.items)
} catch (error) {
  if (error instanceof RateLimitError) {
    // Retry после задержки
  }
}
```

## Стиль документации:

### ✅ Хорошая документация:
- Краткая и по делу
- С примерами кода
- Актуальная (синхронизирована с кодом)
- Объясняет WHY, не только WHAT
- Покрывает edge cases и ошибки

### ❌ Плохая документация:
```python
# Плохо: очевидное
def get_user(id):
    """Gets a user by id"""  # Это и так понятно из названия!

# Хорошо: полезная информация
def get_user(id):
    """
    Получает пользователя из БД с кэшированием.

    Кэш: Redis, TTL 5 минут. При изменении юзера через
    update_user() кэш инвалидируется автоматически.

    Raises: UserNotFoundError если юзер не существует
    """
```

## Приоритеты документации:

1. **High priority** (документируй всегда):
   - Public APIs
   - Сложная бизнес-логика
   - Non-obvious код
   - Configuration опции

2. **Medium priority**:
   - Internal utilities
   - Helper функции
   - Data models

3. **Low priority** (обычно не нужно):
   - Тривиальные getters/setters
   - Самодокументируемый код
   - Приватные implementation details

## Проверь:
- [ ] Примеры кода рабочие (не outdated)
- [ ] Типы параметров указаны
- [ ] Описаны возможные ошибки
- [ ] Есть хотя бы один пример использования
- [ ] README обновлён если изменился public API

Помни: лучшая документация - это понятный код с хорошими именами. Документация нужна там, где код не может объяснить себя сам.
