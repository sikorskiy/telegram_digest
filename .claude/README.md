# Claude Code Setup для эффективной разработки

Этот репозиторий настроен для максимально эффективной работы с Claude Code.

## 📁 Структура

```
.claude/
├── README.md              # Это руководство
├── SETUP_TEMPLATE.md      # Полный шаблон для новых проектов
├── settings.json          # Настройки и хуки
├── commands/              # Slash команды
│   ├── test.md           # /test - запуск тестов
│   ├── review.md         # /review - code review
│   ├── debug.md          # /debug - отладка
│   ├── feature.md        # /feature - новая фича
│   ├── refactor.md       # /refactor - рефакторинг
│   ├── security.md       # /security - аудит безопасности
│   ├── optimize.md       # /optimize - оптимизация
│   ├── docs.md           # /docs - документация
│   ├── explore.md        # /explore - изучение кода
│   ├── commit.md         # /commit - умный коммит
│   ├── productivity.md   # /productivity - советы
│   ├── telegram-bot-init.md  # /telegram-bot-init
│   ├── life-organize.md  # /life-organize
│   ├── quick-script.md   # /quick-script
│   └── automation.md     # /automation
└── hooks/                 # Скрипты для хуков (пусто, можно добавить)
```

## 🚀 Быстрый старт

### 1. Используй команды прямо сейчас

```bash
# Запустить тесты
/test

# Code review изменений
/review

# Отладка
/debug "описание проблемы"

# Создать новую фичу
/feature "описание фичи"

# Рефакторинг
/refactor "путь/к/файлу"

# Security audit
/security "путь/к/файлу"
```

### 2. Проверь настроенные хуки

**PostToolUse** - автоматическое форматирование после редактирования кода:
- Запускает `black` и `isort` для Python
- Или `prettier` для JavaScript
- Или `gofmt` для Go

**PreToolUse** - блокировка опасных команд:
- Защита от `rm -rf /`
- Защита от `DROP DATABASE`
- Защита от force push в main/master

**Stop** - показ git status после завершения работы

### 3. Для новых проектов

Скопируй файлы из этой директории в свой новый проект:

```bash
# Создай новый проект
mkdir ~/my-new-project
cd ~/my-new-project

# Скопируй настройку Claude Code
cp -r /home/user/telegram_digest/.claude .

# Адаптируй CLAUDE.md под свой проект
# (используй SETUP_TEMPLATE.md как референс)
```

## 📚 Описание команд

### Разработка

- **`/test`** - автоматически определяет тип проекта и запускает тесты
- **`/review`** - анализ последних изменений на качество, безопасность, производительность
- **`/debug <описание>`** - помощь в отладке с полным контекстом
- **`/feature <описание>`** - реализация новой фичи с планированием
- **`/refactor <путь>`** - рефакторинг с сохранением функциональности
- **`/explore <путь>`** - изучение структуры проекта/модуля

### Качество кода

- **`/security <путь>`** - аудит безопасности (injection, auth, validation)
- **`/optimize <путь>`** - оптимизация производительности
- **`/docs <путь>`** - генерация/обновление документации
- **`/commit`** - создание осмысленного git commit с анализом изменений

### Продуктивность

- **`/productivity`** - советы по эффективной работе с Claude Code
- **`/telegram-bot-init <библиотека>`** - создание нового Telegram бота
- **`/life-organize`** - настройка системы управления задачами
- **`/quick-script <описание>`** - быстрое создание утилитарного скрипта
- **`/automation <задача>`** - настройка автоматизации рутины

## 🔧 Настройка хуков

### Текущие хуки:

1. **Автоформатирование** (PostToolUse)
   - Срабатывает после изменения файлов в `src/`
   - Запускает форматтеры (black, isort, prettier, gofmt)

2. **Защита от опасных команд** (PreToolUse)
   - Блокирует деструктивные bash команды
   - Exit code 2 = заблокировано

3. **Git status** (Stop)
   - Показывает состояние репозитория после завершения

### Как добавить свои хуки:

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
            "command": "твоя команда тут"
          }
        ]
      }
    ]
  }
}
```

## 💡 Best Practices

### Управление контекстом

```bash
# Проверить размер контекста
/context

# Сжать историю (экономит ~70% токенов)
/compact

# Очистить перед новой задачей
/clear

# Именовать важные сессии
/rename проект-фича-дата

# Возобновить работу
/resume проект-фича-дата
```

### Эффективные промпты

❌ **Плохо:**
```
Исправь баг
```

✅ **Хорошо:**
```
В src/auth.py:42 NullPointerException при пустом пароле.
Добавь проверку и верни ValidationError как в src/validators.py
```

### Workflow

1. **Утром:**
   ```bash
   cd ~/project
   /resume project-name
   /todos
   ```

2. **Новая фича:**
   ```bash
   /clear
   /rename project-auth-feature
   /feature "OAuth2 integration"
   ```

3. **Перед коммитом:**
   ```bash
   /review
   /test
   git add . && git commit -m "..."
   ```

## 📖 Дополнительные ресурсы

- **SETUP_TEMPLATE.md** - полное руководство по настройке
- **CLAUDE.md** (в корне проекта) - контекст текущего проекта
- [Официальная документация](https://code.claude.com/docs)
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)

## 🎯 Следующие шаги

1. Попробуй команды: `/test`, `/review`, `/explore`
2. Адаптируй `CLAUDE.md` под свой проект
3. Добавь свои slash команды для частых задач
4. Настрой дополнительные хуки если нужно
5. Изучи `SETUP_TEMPLATE.md` для продвинутых возможностей

## 🤝 Копирование в другие проекты

Эту настройку можно переиспользовать:

```bash
# Скопировать в другой проект
cp -r .claude ~/other-project/

# Или создать глобальный шаблон
mkdir -p ~/.claude-templates/default
cp -r .claude/* ~/.claude-templates/default/

# В новом проекте:
cp -r ~/.claude-templates/default .claude
```

---

**Готово!** Теперь у тебя есть полноценная настройка Claude Code для эффективной разработки.

Начни с `/test` или `/review` чтобы увидеть команды в действии.
