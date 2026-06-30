#!/bin/bash

# clean.sh - скрипт для удаления мусорных файлов в проекте Avito Commander

echo "🧹 Очистка временных и резервных файлов..."

# Удаляем резервные копии
find . -name "*.backup" -type f -delete
find . -name "*.bak" -type f -delete

# Удаляем временные скрипты (apply_*, fix_*, upgrade_*)
rm -f apply_*.py fix_*.py upgrade_*.py

# Удаляем XML-файлы (фиды Avito)
rm -f avito_feed_*.xml

# Удаляем ZIP-архивы
rm -f *.zip
rm -f chromedriver.zip

# Удаляем chromedriver (если он есть)
rm -f chromedriver

# Удаляем папки с временными данными
rm -rf avitoxml/
rm -rf avitoxml_backup/

# Удаляем прочие файлы
rm -f structure.txt
rm -f clean_project.zip

# Удаляем конкретные резервные копии из корня и папок
rm -f main_app.py.backup
rm -f start_screen.py.backup
rm -f ui/main_window.py.backup
rm -f api/sync_service.py.backup

# Удаляем все __pycache__ папки и .pyc файлы
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -type f -delete

# Удаляем логи
rm -f *.log

echo "✅ Очистка завершена."
echo "📂 Оставшиеся файлы:"
ls -la | grep -v "total" | grep -v "venv" | grep -v ".git" | grep -v ".env" | grep -v "avito_commander.db"
echo
echo "💡 Если вы хотите также удалить .env и avito_commander.db (ВАЖНО: это ваши личные данные!), выполните:"
echo "   rm -f .env avito_commander.db"