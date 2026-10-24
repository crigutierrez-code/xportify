#!/usr/bin/env python3
import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .utils.icon import icono_app


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Xportify")
    app.setOrganizationName("Xportify")
    app.setWindowIcon(icono_app())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
