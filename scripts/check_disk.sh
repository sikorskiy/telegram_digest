#!/bin/bash
# Скрипт для анализа использования диска
# Сохрани как check_disk.sh и запусти: bash check_disk.sh

echo "=== Общее использование диска ==="
df -h

echo -e "\n=== Топ 10 больших директорий в HOME ==="
du -h ~ 2>/dev/null | sort -rh | head -10

echo -e "\n=== Размер общих cache директорий ==="
echo "npm cache:"
du -sh ~/.npm 2>/dev/null || echo "Не найдено"

echo "pip cache:"
du -sh ~/.cache/pip 2>/dev/null || echo "Не найдено"

echo "Docker:"
docker system df 2>/dev/null || echo "Docker не установлен"

echo -e "\n=== Временные файлы ==="
echo "/tmp:"
du -sh /tmp 2>/dev/null || echo "Нет доступа"

echo -e "\n=== Старые логи (>30 дней) ==="
find ~/Library/Logs -type f -mtime +30 2>/dev/null | wc -l || echo "macOS logs"
find ~/.cache -type f -mtime +30 2>/dev/null | wc -l || echo "Linux cache"

echo -e "\n=== Рекомендации готовы! ==="
