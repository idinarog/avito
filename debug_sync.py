#!/usr/bin/env python3
"""
Добавляет отладочные print в синхронизацию и исправляет потенциальные ошибки
"""

import os
import re
import shutil

# Файлы для модификации
files = {
    'main_app.py': {
        'add_prints': True,
        'fix_table': True,
    },
    'api/sync_service.py': {
        'add_prints': True,
        'fix_repo': True,
    }
}

def backup_and_read(path):
    if os.path.exists(path):
        shutil.copy2(path, path + '.debug.bak')
        print(f"✅ Резервная копия {path}.debug.bak создана")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {path} обновлён")

# 1. Добавляем print в main_app.py
path = 'main_app.py'
content = backup_and_read(path)

# В __init__ добавим print
init_pattern = re.compile(r'(def\s+__init__\s*\([^)]*\)\s*:\s*\n)((?:[ \t]+.*\n)*)', re.DOTALL)
match = init_pattern.search(content)
if match:
    body = match.group(2)
    if 'print("🔍 MainApp __init__ started")' not in body:
        lines = body.splitlines()
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('super') or line.strip().startswith('self.init_ui'):
                insert_pos = i + 1
                break
        lines.insert(insert_pos, '        print("🔍 MainApp __init__ started")')
        body = '\n'.join(lines)
        content = content[:match.start()] + match.group(1) + body + content[match.end():]

# В load_items_from_db добавим print
content = content.replace('def load_items_from_db(self):', 'def load_items_from_db(self):\n        print("🔍 load_items_from_db called")')
# В sync_items
content = content.replace('def sync_items(self):', 'def sync_items(self):\n        print("🔄 sync_items called")')
# В _do_sync
content = content.replace('def _do_sync(self):', 'def _do_sync(self):\n        print("⚙️ _do_sync called")')

# Проверим имя таблицы – если self.table не существует, попробуем найти QTableWidget
if 'self.table' in content:
    table_name = 'table'
else:
    # поищем другие имена
    match_table = re.search(r'self\.(\w+)\s*=\s*QTableWidget', content)
    if match_table:
        table_name = match_table.group(1)
        print(f"ℹ️ Найдена таблица: self.{table_name}")
        # Заменим в load_items_from_db self.table на правильное имя
        content = content.replace('self.table', f'self.{table_name}')

write_file(path, content)

# 2. Добавляем print в sync_service.py
path = 'api/sync_service.py'
content = backup_and_read(path)

# В начало sync_all_items добавим print
content = content.replace('def sync_all_items(self, user_id_avito: str) -> int:', 
                          'def sync_all_items(self, user_id_avito: str) -> int:\n        print(f"⚡ sync_all_items called with user_id={user_id_avito}")')

# Также добавим вывод токена
content = content.replace('print(f"🔄 Начинаю синхронизацию для user_id={user_id_avito}...")',
                          'print(f"🔄 Начинаю синхронизацию для user_id={user_id_avito}...")\n        print(f"🔑 Токен в sync_all_items: {self.avito_api.auth.access_token[:10]}...")')

write_file(path, content)

print("\n✅ Отладочные print добавлены. Запустите python3 main.py и войдите, затем покажите весь вывод консоли.")