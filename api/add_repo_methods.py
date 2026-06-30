import re

file = 'database/repository.py'
with open(file, 'r') as f:
    content = f.read()

# Ищем класс ItemRepository
class_start = re.search(r'class ItemRepository\s*:', content)
if not class_start:
    print('❌ Класс ItemRepository не найден')
    exit(1)

# Ищем тело класса — всё до следующего класса или конца файла
class_body = content[class_start.end():]
# Находим конец класса: либо следующий класс с отступом 0, либо конец файла
next_class = re.search(r'\nclass\s+', class_body)
if next_class:
    class_end = class_start.end() + next_class.start()
else:
    class_end = len(content)

class_content = content[class_start.start():class_end]

# Проверяем наличие get_by_user_id
if 'def get_by_user_id' in class_content:
    print('ℹ️ get_by_user_id уже есть, пропускаем')
else:
    # Вставляем метод перед последним '    ' в теле класса
    lines = class_content.splitlines()
    # Находим последнюю строку с отступом (не пустую)
    insert_pos = len(lines)
    for i in range(len(lines)-1, -1, -1):
        if lines[i].strip():
            insert_pos = i + 1
            break
    # Добавляем метод
    method = '''
    def get_by_user_id(self, user_id_avito: str):
        """Возвращает объявления по user_id_avito"""
        cursor = self.db.execute("SELECT * FROM items WHERE user_id_avito = ?", (user_id_avito,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
'''
    lines.insert(insert_pos, method.rstrip())
    new_class_content = '\n'.join(lines)
    new_content = content[:class_start.start()] + new_class_content + content[class_end:]
    with open(file + '.bak', 'w') as f:
        f.write(content)
    with open(file, 'w') as f:
        f.write(new_content)
    print('✅ Добавлен метод get_by_user_id')