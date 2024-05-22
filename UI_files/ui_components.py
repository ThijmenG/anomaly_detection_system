from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
                             QRadioButton, QGroupBox, QHBoxLayout, QLineEdit, QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDateEdit, QSpinBox, QLineEdit
from .data_selection import DataSelectionLabel
from .Results_plot import PlotWindow
from .model_handler import run_model
from Model.data_loader import data_loader
import numpy as np



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dateInputs = []
        self.offlineHoursInputs = []
        self.clogLocationInputs = []  # Add this line
        self.filePath = None  # Initialize self.filePath to None

    def initUI(self):
        self.setWindowTitle('Model Runner Application')
        self.centerWindow()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # File drop label
        self.initFileDrop()

        # Error message label
        self.errorMessageLabel = QLabel(self)
        self.errorMessageLabel.setStyleSheet("color: red;")
        self.errorMessageLabel.hide()  # Initially hide the error message label
        self.layout.addWidget(self.errorMessageLabel)

        # Cloggage question group
        self.initClogQuestionGroup()

        # Layout for dynamically adding date inputs
        self.dateInputLayout = QVBoxLayout()
        self.layout.addLayout(self.dateInputLayout)

        # Button to run the model
        self.initRunModelButton()

    def initFileDrop(self):
        self.fileDropLabel = DataSelectionLabel('Drop your file here or click to select', self)
        self.fileDropLabel.fileSelected.connect(self.enableRunModelButton)
        self.fileDropLabel.invalidFileSelected.connect(self.showErrorMessage)  # Connect signal to slot
        self.layout.addWidget(self.fileDropLabel)

    def showErrorMessage(self, message):
        self.errorMessageLabel.setText(message)
        self.errorMessageLabel.show()


    def initClogQuestionGroup(self):
        self.clogQuestionGroup = QGroupBox("Has there been any cloggages in this period?")
        clogLayout = QHBoxLayout()
        self.yesButton = QRadioButton("Yes")
        self.noButton = QRadioButton("No")
        self.noButton.setChecked(True)
        clogLayout.addWidget(self.yesButton)
        clogLayout.addWidget(self.noButton)
        clogLayout.addStretch(1)
        self.clogQuestionGroup.setLayout(clogLayout)
        self.clogQuestionGroup.setFixedHeight(100)  # Fix the height to prevent resizing
        self.layout.addWidget(self.clogQuestionGroup)

        self.addDateButton = QPushButton('Add Date', self)
        self.addDateButton.clicked.connect(self.addDateInput)
        self.addDateButton.setEnabled(False)
        self.yesButton.toggled.connect(self.enableAddDate)
        self.layout.addWidget(self.addDateButton)


    def enableRunModelButton(self, filePath):
        self.filePath = filePath
        self.errorMessageLabel.hide()  # Hide error message when a valid file is selected
        self.runModelButton.setEnabled(True)

    def initRunModelButton(self):
        self.runModelButton = QPushButton('Run Model', self)
        self.runModelButton.setEnabled(False)
        self.layout.addWidget(self.runModelButton)
        self.runModelButton.clicked.connect(self.runModel)

    def initHeaderRow(self):
        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, -10)  # Reduce the bottom margin to bring headers closer to the rows
        headerLayout.setSpacing(1)

        dateLabel = QLabel("Date")
        hoursLabel = QLabel("Offline Hours")
        locationLabel = QLabel("Clog Location (optional)")

        headerLayout.addWidget(dateLabel, 2)
        headerLayout.addWidget(hoursLabel, 1)
        headerLayout.addWidget(locationLabel, 3)

        self.dateInputLayout.addLayout(headerLayout)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setGeometry(qr)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setGeometry(qr)

    def enableAddDate(self, enabled):
        self.addDateButton.setEnabled(enabled)
        if enabled:
            # 'Yes' is selected, add a standard row
            self.addDateInput()
        else:
            # 'No' is selected, remove all date rows
            while self.dateInputLayout.count():
                child = self.dateInputLayout.takeAt(0)
                if child:
                    # Check if the child is a layout (which contains the date, hours, and location inputs)
                    if isinstance(child, QHBoxLayout):
                        while child.count():
                            subChild = child.takeAt(0).widget()
                            if subChild:
                                subChild.deleteLater()
                    else:
                        child.widget().deleteLater()

    def addDateInput(self):
        if self.dateInputLayout.count() == 0:
            self.initHeaderRow()

        rowLayout = QHBoxLayout()
        rowLayout.setContentsMargins(0, 5, 0, 5)  # Adjust top and bottom margins to reduce space

        dateInput = QDateEdit()
        dateInput.setDate(QDate.currentDate())
        dateInput.setCalendarPopup(True)
        dateInput.dateChanged.connect(self.checkInputs)  # Connect the dateChanged signal to checkInputs
        rowLayout.addWidget(dateInput, 2)
        self.dateInputs.append(dateInput)  # Store a reference to the dateInput

        offlineHoursInput = QSpinBox()
        offlineHoursInput.setRange(0, 24)
        offlineHoursInput.valueChanged.connect(self.checkInputs)  # Connect the valueChanged signal to checkInputs
        rowLayout.addWidget(offlineHoursInput, 1)
        self.offlineHoursInputs.append(offlineHoursInput)  # Store a reference to the offlineHoursInput

        clogLocationInput = QLineEdit()
        clogLocationInput.setPlaceholderText("Enter clog location (optional)")
        rowLayout.addWidget(clogLocationInput, 3)
        self.clogLocationInputs.append(clogLocationInput)  # Add this line


        self.dateInputLayout.addLayout(rowLayout)

    def checkInputs(self):
        if self.filePath is None:  # Check if a file has been selected
            self.runModelButton.setEnabled(False)
            return

        for dateInput, offlineHoursInput in zip(self.dateInputs, self.offlineHoursInputs):
            if dateInput.date() == QDate() or offlineHoursInput.value() <= 0 or self.filePath is None:
                self.runModelButton.setEnabled(False)
                return
        self.runModelButton.setEnabled(True)

    def runModel(self):
        print('got to runModel')

        new_data = data_loader(self.filePath)  # Load data using the data_loader function
        print(new_data.head())

        if self.noButton.isChecked():
            print('no button checked')
            processed_data, predictions = run_model(self.filePath, new_data)
            self.resultWindow = PlotWindow(processed_data, predictions)
            self.resultWindow.show()
        else:
            data = {
                'Date': [dateInput.date().toPyDate() for dateInput in self.dateInputs],
                'Offline Hours': [offlineHoursInput.value() for offlineHoursInput in self.offlineHoursInputs],
                'Clog Location': [clogLocationInput.text() for clogLocationInput in self.clogLocationInputs]
            }
            clog_data = pd.DataFrame(data)
            processed_data, predictions = run_model(self.filePath, new_data)

            self.resultWindow = PlotWindow(processed_data, predictions, clog_data=clog_data)
            self.resultWindow.show()


