import os

T = "/Users/stanislav.kuznetsov/avito_commander"
DIRS = ["core", "database", "api", "ui", "ui/widgets", "ui/dialogs", "services", "utils", "assets", "assets/icons", "assets/styles", "tests"]
FILES = ["main.py", "config.py", "requirements.txt", ".env", "avito_commander.db", "core/__init__.py", "core/app.py", "core/config_manager.py", "core/event_bus.py", "database/__init__.py", "database/models.py", "database/repository.py", "database/migration.py", "api/__init__.py", "api/avito_api.py", "api/sync_service.py", "api/telegram_bot.py", "ui/__init__.py", "ui/main_window.py", "ui/login_dialog.py", "ui/widgets/__init__.py", "ui/widgets/item_table.py", "ui/widgets/filter_panel.py", "ui/widgets/stats_widget.py", "ui/widgets/status_bar.py", "ui/dialogs/__init__.py", "ui/dialogs/item_dialog.py", "ui/dialogs/settings_dialog.py", "ui/dialogs/import_export.py", "services/__init__.py", "services/item_service.py", "services/project_service.py", "services/analytics_service.py", "services/notification_service.py", "utils/__init__.py", "utils/logger.py", "utils/helpers.py", "utils/validators.py", "assets/splash.png", "tests/__init__.py", "tests/test_api.py", "tests/test_database.py", "tests/test_services.py"]

os.makedirs(T, exist_ok=True)
for d in DIRS: 
    os.makedirs(os.path.join(T, d), exist_ok=True)

for f in FILES:
    p = os.path.join(T, f)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as fp: 
            if f.endswith(".py") and not f.endswith("__init__.py"): 
                fp.write(f"# {f}\n")
        print(f"Создан: {f}")

print("Структура успешно проверена и досоздана!")
