import os
from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal


class DataSelectionLabel(QLabel):
    fileSelected = pyqtSignal(str)  # Signal that emits the file path when a file is selected

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
            self.filePath = urls[0].toLocalFile()
            self.updateFileSelection(self.filePath)

    def mousePressEvent(self, event):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a file", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.updateFileSelection(fileName)


    def updateFileSelection(self, filePath):
        self.filePath = filePath
        self.setText(f"Selected File: {os.path.basename(self.filePath)}")
        self.setStyleSheet("background-color: #90EE90")  # Light green
        self.fileSelected.emit(self.filePath)  #

