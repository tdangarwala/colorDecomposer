import sys
from ColorPickerApp import ColorPickerApp

from PyQt6.QtWidgets import QApplication 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorPickerApp()
    window.show()
    sys.exit(app.exec())
