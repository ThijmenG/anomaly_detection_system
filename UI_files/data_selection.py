import os
from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal


class DataSelectionLabel(QLabel):
    """ QLabel subclass that allows users to select a file by dragging and dropping or clicking on the label."""

    fileSelected = pyqtSignal(str)  # Signal that emits the file path when a file is selected
    invalidFileSelected = pyqtSignal(str)  # Signal that emits an error message when an invalid file is selected

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
        self.setFixedSize(600, 150)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            urls = event.mimeData().urls()
            filePath = urls[0].toLocalFile()
            if filePath.endswith(('.csv', '.xlsx')):
                self.updateFileSelection(filePath)
            else:
                self.invalidFileSelected.emit("Invalid file type. Please select a CSV or Excel file.")  # Emit signal

    def mousePressEvent(self, event):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a file", "",
                                                  "CSV or Excel Files (*.csv *.xlsx)", options=options)
        if fileName and fileName.endswith(('.csv', '.xlsx')):
            self.updateFileSelection(fileName)
        elif fileName:
            self.invalidFileSelected.emit("Invalid file type. Please select a CSV or Excel file.")  # Emit signal

    def updateFileSelection(self, filePath):
        self.filePath = filePath
        self.setText(f"Selected File: {os.path.basename(self.filePath)}")
        self.setStyleSheet("background-color: #90EE90")  # Light green
        self.fileSelected.emit(self.filePath)
