import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("OK WORKS")
label.resize(200, 100)
label.show()
sys.exit(app.exec_())