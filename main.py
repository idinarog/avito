import sys
from PyQt5.QtWidgets import QApplication
from start_screen import StartScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = StartScreen()
    window.show()

    sys.exit(app.exec_())