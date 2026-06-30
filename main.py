import sys
from PyQt5.QtWidgets import QApplication
from start_screen import StartScreen
from core.app import app as core_app

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)

# 🎨 подключаем стиль
with open("assets/styles/main.qss") as f:
    qt_app.setStyleSheet(f.read())


    core_app.init_app()
    window = StartScreen(core_app)
    window.show()

    sys.exit(qt_app.exec_())
print("START APP")

from ui.login_dialog import LoginDialog

dialog = LoginDialog()
print("OPEN DIALOG")
dialog.exec_()
print("AFTER DIALOG")
