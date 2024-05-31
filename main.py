import sys
from PyQt5.QtWidgets import QApplication
from UI_files.ui_components import MainWindow  # Ensure this import is correct
from UI_files.resource_path import resource_path

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the stylesheet using resource_path
    stylesheet_path = resource_path("UI_files/stylesheet.qss")
    with open(stylesheet_path, "r") as style_file:
        app.setStyleSheet(style_file.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
