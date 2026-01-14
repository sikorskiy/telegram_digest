# ⚡ Быстрый старт за 5 минут

## 1️⃣ Установка (30 секунд)

```bash
# В существующий проект
cd your-project
git clone https://github.com/YOUR_USERNAME/claude-code-setup.git temp
cp -r temp/.claude .
cp temp/CLAUDE.md.example CLAUDE.md
rm -rf temp

# ИЛИ новый проект
git clone https://github.com/YOUR_USERNAME/claude-code-setup.git my-project
cd my-project
rm -rf .git
git init
mv CLAUDE.md.example CLAUDE.md
```

## 2️⃣ Адаптация CLAUDE.md (2 минуты)

Открой `CLAUDE.md` и замени:

```markdown
# [Твой проект] - Контекст для Claude

## Цель проекта
Telegram бот для управления задачами

## Технологии
- Python 3.11 + aiogram
- PostgreSQL
- Redis для кэша

## Основные файлы
- bot/handlers/ - обработчики команд
- bot/database/ - модели БД
- main.py - entry point

## Команды
```bash
python main.py  # Запуск
pytest          # Тесты
```

Готово! Claude теперь понимает твой проект.

## 3️⃣ Первое использование (2 минуты)

### Попробуй команды:

```bash
# Запустить тесты
/test

# Code review последних изменений
/review

# Изучить структуру проекта
/explore src/

# Получить все советы по продуктивности
/productivity
```

### Эффективный промпт:

```
/feature "Добавь команду /tasks в Telegram бота, которая:
- Показывает список задач из PostgreSQL
- Фильтрует по статусу (todo/done)
- Выводит в виде inline keyboard
Используй существующий паттерн из handlers/start.py"
```

Claude:
1. Изучит структуру проекта
2. Прочитает существующий код
3. Создаст план
4. Реализует фичу
5. Добавит обработку ошибок

## 4️⃣ Автоматизация (1 минута)

Уже работает из коробки:

✅ **Автоформатирование** после каждого редактирования
- Python: black, isort
- JS: prettier
- Go: gofmt

✅ **Защита** от опасных команд
- Блокирует `rm -rf /`
- Блокирует force push в main

✅ **Git status** после завершения работы

## 🎯 Частые сценарии

### Новая фича
```bash
/clear                          # Свежий контекст
/rename myapp-payment-feature   # Имя сессии
/feature "OAuth2 + Stripe"      # Описание
```

### Отладка
```bash
/debug "Error в user.py:42 - NullPointerException
Стек: [вставить]
Воспроизводится при пустом email"
```

### Code review перед коммитом
```bash
git add .
/review
# Исправляем замечания
/test
/commit
```

### Создать Telegram бота
```bash
/telegram-bot-init aiogram
# Claude создаст полную структуру
```

## 💡 Pro Tips

### Управление контекстом
```bash
/context   # Проверить размер
/compact   # Сжать (экономит 70%)
/clear     # Очистить перед новой задачей
```

### Эффективные промпты

❌ Плохо:
```
Исправь баг
```

✅ Хорошо:
```
В src/auth.py:42 получаю NullPointerException при пустом пароле.
Добавь проверку и верни ValidationError, как в src/validators.py:15
```

### Сессии для долгих задач
```bash
# Начало работы
/rename myapp-auth-feature

# На следующий день
/resume myapp-auth-feature
# Продолжаешь с того же места
```

## 📚 Все команды

| Команда | Что делает |
|---------|-----------|
| `/test` | Запускает тесты |
| `/review` | Code review изменений |
| `/debug <описание>` | Помощь в отладке |
| `/feature <описание>` | Реализует новую фичу |
| `/refactor <путь>` | Рефакторит код |
| `/security <путь>` | Security audit |
| `/optimize <путь>` | Оптимизирует производительность |
| `/docs <путь>` | Генерирует документацию |
| `/explore <путь>` | Изучает структуру |
| `/commit` | Создаёт умный коммит |
| `/productivity` | Все советы по эффективности |
| `/telegram-bot-init` | Создаёт Telegram бота |
| `/life-organize` | Система управления задачами |
| `/quick-script` | Быстрый утилитарный скрипт |
| `/automation` | Настройка автоматизации |

## 🚀 Следующие шаги

1. **Попробуй 3-4 команды** прямо сейчас
2. **Прочитай `/productivity`** - получишь полное руководство
3. **Адаптируй под себя** - добавь свои команды в `.claude/commands/`
4. **Поделись опытом** - расскажи что работает, а что можно улучшить

## ❓ Проблемы?

**Команда не работает:**
- Проверь что файл существует: `ls .claude/commands/`
- Убедись что формат правильный (YAML frontmatter)

**Хуки не срабатывают:**
- Проверь `.claude/settings.json`
- Убедись что форматтеры установлены (`black`, `prettier`)

**Контекст переполнен:**
- Используй `/compact` регулярно
- Или `/clear` между крупными задачами

## 📖 Документация

- **README.md** - полное описание репозитория
- **.claude/README.md** - справка по командам
- **.claude/SETUP_TEMPLATE.md** - глубокое погружение (80+ страниц)

---

**Готово!** Теперь у тебя суперсила в виде 16 команд и автоматизации.

Начни с `/test` или `/review` 🚀
