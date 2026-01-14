# 🚀 Claude Code Setup - Готовая конфигурация для эффективной разработки

> Полноценная настройка Claude Code с 16 slash-командами, хуками и шаблонами для максимальной продуктивности

## 📋 Что это?

Это **готовый к использованию шаблон** для настройки Claude Code в любом проекте. Включает:

- ✅ **16 универсальных slash-команд** для разработки, отладки, code review
- ✅ **Автоматические хуки** для форматирования кода и безопасности
- ✅ **Шаблон CLAUDE.md** для быстрого старта в новом проекте
- ✅ **Полное руководство** по эффективной работе (80+ страниц)

## 🎯 Быстрый старт

### Вариант 1: Клонировать в существующий проект

```bash
cd your-project
git clone https://github.com/USERNAME/claude-code-setup.git temp-claude
cp -r temp-claude/.claude .
cp temp-claude/CLAUDE.md.example CLAUDE.md
rm -rf temp-claude

# Адаптируй CLAUDE.md под свой проект
nano CLAUDE.md
```

### Вариант 2: Начать новый проект с этим шаблоном

```bash
git clone https://github.com/USERNAME/claude-code-setup.git my-new-project
cd my-new-project
rm -rf .git
git init
mv CLAUDE.md.example CLAUDE.md

# Адаптируй CLAUDE.md под свой проект
nano CLAUDE.md

git add .
git commit -m "Initial commit with Claude Code setup"
```

### Вариант 3: Глобальный шаблон

```bash
# Сохрани как шаблон
mkdir -p ~/.claude-templates
git clone https://github.com/USERNAME/claude-code-setup.git ~/.claude-templates/default

# В любом новом проекте
cd your-project
cp -r ~/.claude-templates/default/.claude .
cp ~/.claude-templates/default/CLAUDE.md.example CLAUDE.md
```

## 📚 Что включено?

### 🎨 Slash-команды (16 штук)

#### Разработка
- `/test` - Автоматический запуск тестов (определяет тип проекта)
- `/review` - Code review изменений (качество, безопасность, производительность)
- `/debug <описание>` - Помощь в отладке с полным контекстом
- `/feature <описание>` - Реализация новой фичи с планированием
- `/refactor <путь>` - Рефакторинг с сохранением функциональности
- `/explore <путь>` - Изучение структуры проекта/модуля

#### Качество кода
- `/security <путь>` - Security audit (injection, auth, validation)
- `/optimize <путь>` - Оптимизация производительности
- `/docs <путь>` - Генерация/обновление документации
- `/commit` - Создание осмысленного git commit с анализом

#### Продуктивность & Автоматизация
- `/productivity` - Полное руководство по эффективной работе
- `/telegram-bot-init` - Создание структуры Telegram бота
- `/life-organize` - Система управления личными задачами
- `/quick-script` - Быстрое создание утилитарных скриптов
- `/automation` - Настройка автоматизации рутинных задач

### 🔧 Автоматические хуки

**PostToolUse** - Автоформатирование после редактирования:
- Python: `black`, `isort`
- JavaScript/TypeScript: `prettier`
- Go: `gofmt`

**PreToolUse** - Защита от опасных команд:
- Блокировка `rm -rf /`
- Блокировка `DROP DATABASE`
- Блокировка force push в main/master

**Stop** - Показ git status после завершения работы

### 📖 Документация

- **`.claude/README.md`** - Быстрый старт и справка по командам
- **`.claude/SETUP_TEMPLATE.md`** - Полное руководство (80+ страниц)
- **`CLAUDE.md.example`** - Шаблон для вашего проекта

## 💡 Примеры использования

### Code Review перед коммитом
```bash
# Сделал изменения
git add .

# Проверка
/review

# Исправил замечания, запустил тесты
/test

# Умный коммит
/commit
```

### Новая фича
```bash
/clear  # Свежий контекст
/rename myproject-auth-feature

# Подробное описание
/feature "Реализуй JWT аутентификацию с refresh токенами"

# Claude создаёт план и реализует
# Тестируем
/test

# Review
/review
```

### Отладка бага
```bash
/debug "В src/auth.py:42 NullPointerException при пустом пароле.
Стек: [вставить стек трейс]
Воспроизводится когда user вводит пустую строку"

# Claude анализирует и предлагает фикс
```

### Создание Telegram бота
```bash
/telegram-bot-init aiogram

# Claude создаст полную структуру проекта с handlers, keyboards, middleware
```

### Автоматизация рутины
```bash
/automation "Настрой отправку ежедневного отчёта в Telegram в 9:00"

# Claude создаст скрипт + cron настройку
```

## 🎓 Эффективные практики

### Управление контекстом
```bash
/context   # Проверить размер контекста
/compact   # Сжать историю (экономит ~70% токенов)
/clear     # Очистить перед новой задачей
/rename    # Именовать важные сессии
/resume    # Возобновить работу
```

### Эффективные промпты

❌ **Неэффективно:**
```
"Исправь баг"
"Оптимизируй код"
```

✅ **Эффективно:**
```
"В src/auth.py:42 NullPointerException при пустом пароле.
Добавь проверку и верни ValidationError как в src/validators.py"

"Функция process_data() работает 5 сек на 1000 элементах.
Оптимизируй до <1 сек используя батчинг или кэширование"
```

## 🛠 Кастомизация

### Добавить свою команду

Создай файл `.claude/commands/my-command.md`:

```markdown
---
description: Описание команды
---

# Моя команда

Инструкции для Claude что делать при вызове /my-command

$ARGUMENTS - можно использовать аргументы
```

### Настроить хуки

Отредактируй `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "src/",
        "hooks": [
          {
            "type": "command",
            "command": "ваша команда"
          }
        ]
      }
    ]
  }
}
```

### Адаптировать CLAUDE.md

Используй `CLAUDE.md.example` как основу и адаптируй под свой проект:

```markdown
# Ваш проект - Контекст для Claude

## Цель проекта
[В 2-3 предложениях]

## Архитектура
[Основные компоненты]

## Ключевые файлы
- путь/к/файлу - описание

## Технологии
- Язык, фреймворки, БД

## Команды
```bash
npm run dev
npm test
```

## Важные детали
[Специфика проекта]
```

## 📦 Структура репозитория

```
claude-code-setup/
├── README.md                    # Это файл
├── CLAUDE.md.example            # Шаблон для вашего проекта
├── .claude/
│   ├── README.md               # Быстрая справка
│   ├── SETUP_TEMPLATE.md       # Полное руководство (80+ страниц)
│   ├── settings.json           # Настройки и хуки
│   ├── commands/               # 16 slash-команд
│   │   ├── test.md
│   │   ├── review.md
│   │   ├── debug.md
│   │   ├── feature.md
│   │   ├── refactor.md
│   │   ├── security.md
│   │   ├── optimize.md
│   │   ├── docs.md
│   │   ├── explore.md
│   │   ├── commit.md
│   │   ├── productivity.md
│   │   ├── telegram-bot-init.md
│   │   ├── life-organize.md
│   │   ├── quick-script.md
│   │   └── automation.md
│   └── hooks/                  # Место для ваших скриптов
└── .gitignore
```

## 🌟 Особенности

### Универсальность
- Работает с любым языком программирования
- Автоопределение типа проекта (Python/Node.js/Go/Rust)
- Адаптируется под ваш workflow

### Продуктивность
- Slash-команды сокращают рутинные промпты
- Хуки автоматизируют форматирование и проверки
- `/compact` экономит до 70% токенов

### Готово к использованию
- Не требует настройки "из коробки"
- Полная документация включена
- Примеры использования для каждой команды

### Расширяемость
- Легко добавлять свои команды
- Гибкая система хуков
- Можно адаптировать под team workflow

## 🚀 Use Cases

### Для индивидуальных разработчиков
- Ускорение рутинных задач (review, test, debug)
- Организация личных проектов
- Автоматизация жизни через код

### Для команд
- Единый стандарт работы с Claude Code
- Code review перед PR
- Onboarding новых разработчиков

### Для фрилансеров
- Быстрый старт новых проектов
- Шаблоны для типовых задач (Telegram боты, веб-приложения)
- Автоматизация рутины

### Для обучения
- Изучение best practices
- Примеры эффективных промптов
- Руководство по Claude Code

## 📚 Дополнительные ресурсы

- [Официальная документация Claude Code](https://code.claude.com/docs)
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

## 🤝 Contributing

Нашёл улучшение? Создай PR с новой командой или доработкой!

Идеи для новых команд:
- Специфичные для фреймворков (Django, React, FastAPI)
- Деплой и DevOps операции
- Data Science и ML workflow
- Работа с API и интеграциями

## 📝 License

MIT License - используй свободно в своих проектах!

## 🙏 Благодарности

Создано с помощью Claude Code для эффективной разработки.

---

**Начни прямо сейчас:**
```bash
git clone https://github.com/USERNAME/claude-code-setup.git
cd claude-code-setup
cat .claude/README.md  # Быстрый старт
```

**Попробуй команды:**
```bash
/productivity  # Полное руководство по эффективности
/test          # Запустить тесты
/review        # Code review
```

Приятной разработки! 🚀
