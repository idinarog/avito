#!/bin/bash

# Создание структуры директорий
mkdir -p core api services ui scripts config logs

# Создание файлов
touch main.py
touch core/app.py core/state.py
touch api/avito.py
touch services/auth.py services/items.py services/stats.py
touch ui/tui.py ui/input.py
touch scripts/tz_final_working.sh scripts/tz_xml_working.sh
touch config/config.json
touch logs/app.log

# Наполнение .env
cat << 'EOF' > .env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
EOF

# Наполнение requirements.txt
cat << 'EOF' > requirements.txt
requests>=2.31.0
python-dotenv>=1.0.0
EOF

# Наполнение .gitignore
cat << 'EOF' > .gitignore
.env
config/config.json
logs/
__pycache__/
*.pyc
EOF

# Наполнение Makefile (с правильными табами)
cat << 'EOF' > Makefile
run:
	python main.py

install:
	pip install -r requirements.txt
EOF

echo "Структура проекта готова!"

