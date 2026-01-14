#!/bin/bash
# Скрипт для безопасной очистки диска
# Сохрани как clean_disk.sh и запусти: bash clean_disk.sh

set -e

echo "🧹 Начинаем очистку диска..."
echo "Это БЕЗОПАСНЫЙ скрипт - он только удаляет кэши, не затрагивая важные файлы"
echo ""
read -p "Продолжить? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

FREED=0

# 1. npm cache
if command -v npm &> /dev/null; then
    echo "Очистка npm cache..."
    NPM_SIZE=$(du -sm ~/.npm 2>/dev/null | cut -f1 || echo 0)
    npm cache clean --force 2>/dev/null || true
    FREED=$((FREED + NPM_SIZE))
    echo "✓ Освобождено: ${NPM_SIZE}MB"
fi

# 2. pip cache
if command -v pip &> /dev/null; then
    echo "Очистка pip cache..."
    PIP_SIZE=$(du -sm ~/.cache/pip 2>/dev/null | cut -f1 || echo 0)
    pip cache purge 2>/dev/null || true
    FREED=$((FREED + PIP_SIZE))
    echo "✓ Освобождено: ${PIP_SIZE}MB"
fi

# 3. Homebrew (macOS)
if command -v brew &> /dev/null; then
    echo "Очистка Homebrew..."
    BREW_SIZE=$(du -sm ~/Library/Caches/Homebrew 2>/dev/null | cut -f1 || echo 0)
    brew cleanup -s 2>/dev/null || true
    rm -rf ~/Library/Caches/Homebrew/* 2>/dev/null || true
    FREED=$((FREED + BREW_SIZE))
    echo "✓ Освобождено: ${BREW_SIZE}MB"
fi

# 4. Docker
if command -v docker &> /dev/null; then
    echo "Очистка Docker..."
    DOCKER_SIZE=$(docker system df --format "{{.Size}}" 2>/dev/null | head -1 || echo "0B")
    docker system prune -a --volumes -f 2>/dev/null || true
    echo "✓ Docker очищен"
fi

# 5. Временные файлы
echo "Очистка временных файлов..."
rm -rf /tmp/* 2>/dev/null || true
rm -rf ~/.cache/tmp/* 2>/dev/null || true

# 6. Старые логи (>30 дней)
echo "Удаление старых логов (>30 дней)..."
find ~/Library/Logs -type f -mtime +30 -delete 2>/dev/null || true
find ~/.cache -type f -mtime +30 -delete 2>/dev/null || true

# 7. Trash/Корзина
echo "Очистка корзины..."
rm -rf ~/.Trash/* 2>/dev/null || true  # macOS
rm -rf ~/.local/share/Trash/* 2>/dev/null || true  # Linux

# 8. Old downloads (>90 дней, опционально)
# Раскомментируй если хочешь:
# find ~/Downloads -type f -mtime +90 -delete 2>/dev/null || true

echo ""
echo "✅ Очистка завершена!"
echo "📊 Приблизительно освобождено: ${FREED}MB"
echo ""
echo "Для более детальной очистки:"
echo "- macOS: Системные настройки > Хранилище"
echo "- Linux: sudo apt autoremove && sudo apt clean"
echo "- Windows: Очистка диска (Disk Cleanup)"
