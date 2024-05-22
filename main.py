import sys
from PyQt5.QtWidgets import QApplication
from UI_files.ui_components import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the stylesheet
    with open("UI_files/stylesheet.qss", "r") as style_file:
        app.setStyleSheet(style_file.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())