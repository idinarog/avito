import os

# Что заменяем
REPLACEMENTS = {
    "from PyQt5": "from PyQt5",
    "import PyQt5": "import PyQt5",

    "Qt.": "Qt.",
    "Qt.": "Qt.",

    "exec_()": "exec_()",
}

# Папки, которые игнорируем
IGNORE_DIRS = {"venv", "__pycache__", ".git"}

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Обновлён: {path}")


def walk_project(root="."):
    for root_dir, dirs, files in os.walk(root):
        # игнорируем лишнее
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root_dir, file)
                process_file(path)


if __name__ == "__main__":
    print("🔄 Миграция PyQt6 → PyQt5...")
    walk_project()
    print("✅ Готово!")
