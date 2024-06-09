from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
                             QRadioButton, QGroupBox, QHBoxLayout, QLineEdit, QApplication, QDesktopWidget,
                             QDateEdit, QSpinBox, QScrollArea, QComboBox)

from .data_selection import DataSelectionLabel
from .Results_plot import PlotWindow
from .model_handler import run_model
from Model.data_loader import data_loader
from UI_files.resource_path import resource_path
import pandas as pd


class MainWindow(QMainWindow):
    """ Main window for the application."""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dateInputs = []
        self.offlineHoursInputs = []
        self.clogLocationInputs = []
        self.filePath = None

    def initUI(self):
        self.setWindowTitle('Anomaly Detection System')
        self.centerWindow()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # Pressure threshold dropdown
        self.initPressureThresholdDropdown()

        # File drop label
        self.initFileDrop()

        # Error message label
        self.errorMessageLabel = QLabel(self)
        self.errorMessageLabel.setStyleSheet("color: red;")
        self.errorMessageLabel.hide()
        self.layout.addWidget(self.errorMessageLabel)

        # Cloggage question group
        self.initClogQuestionGroup()

        # Scroll area for dynamically adding date inputs
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaContent = QWidget(self.scrollArea)
        self.scrollAreaLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollArea.setWidget(self.scrollAreaContent)
        self.layout.addWidget(self.scrollArea)

        # Buttons to add and remove date inputs
        self.initDateButtons()

        # Button to run the model
        self.initRunModelButton()

    def initPressureThresholdDropdown(self):
        pressureLayout = QHBoxLayout()
        pressureLabel = QLabel("Select Pressure Threshold:")
        self.pressureDropdown = QComboBox(self)
        self.pressureDropdown.addItems(["-0.2", "-0.25", "-0.3"])
        self.pressureDropdown.setCurrentIndex(1)  # Set "Medium" as the default selection

        pressureLayout.addWidget(pressureLabel)
        pressureLayout.addWidget(self.pressureDropdown)
        self.layout.addLayout(pressureLayout)

    def initFileDrop(self):
        self.fileDropLabel = DataSelectionLabel('Drop your file here or click to select', self)
        self.fileDropLabel.fileSelected.connect(self.enableRunModelButton)
        self.fileDropLabel.invalidFileSelected.connect(self.showErrorMessage)
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
        self.clogQuestionGroup.setFixedHeight(100)
        self.layout.addWidget(self.clogQuestionGroup)

        self.yesButton.toggled.connect(self.enableAddDate)

    def enableRunModelButton(self, filePath):
        self.filePath = filePath
        self.errorMessageLabel.hide()
        self.runModelButton.setEnabled(True)

    def initRunModelButton(self):
        self.runModelButton = QPushButton('Run Model', self)
        self.runModelButton.setEnabled(False)
        self.layout.addWidget(self.runModelButton)
        self.runModelButton.clicked.connect(self.runModel)

    def initHeaderRow(self):
        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, -10)

        dateLabel = QLabel("Date")
        hoursLabel = QLabel("Offline Hours")
        locationLabel = QLabel("Clog Location (optional)")

        headerLayout.addWidget(dateLabel, 2)
        headerLayout.addWidget(hoursLabel, 1)
        headerLayout.addWidget(locationLabel, 3)

        self.scrollAreaLayout.addLayout(headerLayout)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setGeometry(qr)

    def enableAddDate(self, enabled):
        self.addDateButton.setEnabled(enabled)
        self.removeDateButton.setVisible(enabled)  # Show or hide the remove button based on the toggle

        if enabled:
            if not self.dateInputs:
                self.addDateInput()
        else:
            self.clearDateInputs()

    def clearDateInputs(self):
        while self.scrollAreaLayout.count():
            child = self.scrollAreaLayout.takeAt(0)
            if child:
                if isinstance(child, QHBoxLayout):
                    while child.count():
                        subChild = child.takeAt(0).widget()
                        if subChild:
                            subChild.deleteLater()
                else:
                    child.widget().deleteLater()
        self.dateInputs.clear()
        self.offlineHoursInputs.clear()
        self.clogLocationInputs.clear()

    def addDateInput(self):
        if not self.dateInputs:
            self.initHeaderRow()

        if len(self.dateInputs) < 5:
            rowLayout = QHBoxLayout()
            rowLayout.setContentsMargins(0, 5, 0, 5)

            dateInput = QDateEdit()
            dateInput.setDate(QDate.currentDate())
            dateInput.setCalendarPopup(True)
            dateInput.dateChanged.connect(self.checkInputs)
            rowLayout.addWidget(dateInput, 2)
            self.dateInputs.append(dateInput)

            offlineHoursInput = QSpinBox()
            offlineHoursInput.setRange(0, 24)
            offlineHoursInput.valueChanged.connect(self.checkInputs)
            rowLayout.addWidget(offlineHoursInput, 1)
            self.offlineHoursInputs.append(offlineHoursInput)

            clogLocationInput = QLineEdit()
            clogLocationInput.setPlaceholderText("Enter clog location (optional)")
            rowLayout.addWidget(clogLocationInput, 3)
            self.clogLocationInputs.append(clogLocationInput)

            self.scrollAreaLayout.addLayout(rowLayout)
            self.removeDateButton.setVisible(True)  # Ensure the remove button is visible

        self.scrollArea.setFixedHeight(5 * 35)  # Approximate height for 5 rows

    def removeDateInput(self):
        if self.dateInputs:
            self.dateInputs.pop().deleteLater()
            self.offlineHoursInputs.pop().deleteLater()
            self.clogLocationInputs.pop().deleteLater()
            self.scrollAreaLayout.takeAt(self.scrollAreaLayout.count() - 1).deleteLater()

            if not self.dateInputs:
                self.clearDateInputs()
                self.removeDateButton.setVisible(False)

    def checkInputs(self):
        if not self.filePath:
            self.runModelButton.setEnabled(False)
            return

        for dateInput, offlineHoursInput in zip(self.dateInputs, self.offlineHoursInputs):
            if dateInput.date() == QDate() or offlineHoursInput.value() <= 0 or self.filePath is None:
                self.runModelButton.setEnabled(False)
                return
        self.runModelButton.setEnabled(True)

    def runModel(self):
        print('got to runModel')

        resolved_file_path = resource_path(self.filePath)
        print(resolved_file_path)
        new_data = data_loader(resolved_file_path)
        print(new_data.head())

        pressure_threshold = float(self.pressureDropdown.currentText())


        if self.noButton.isChecked():
            print('no button checked')
            processed_data, predictions = run_model(resolved_file_path, new_data, pressure_threshold)
            self.resultWindow = PlotWindow(processed_data, predictions)
            self.resultWindow.show()
        else:
            data = {
                'Date': [dateInput.date().toPyDate() for dateInput in self.dateInputs],
                'Offline Hours': [offlineHoursInput.value() for offlineHoursInput in self.offlineHoursInputs],
                'Clog Location': [clogLocationInput.text() for clogLocationInput in self.clogLocationInputs]
            }
            clog_data = pd.DataFrame(data)
            processed_data, predictions = run_model(resolved_file_path, new_data, pressure_threshold)

            self.resultWindow = PlotWindow(processed_data, predictions, clog_data=clog_data)
            self.resultWindow.show()

    def initDateButtons(self):
        dateButtonLayout = QHBoxLayout()
        self.addDateButton = QPushButton('Add Date', self)
        self.addDateButton.setEnabled(False)
        self.addDateButton.clicked.connect(self.addDateInput)
        dateButtonLayout.addWidget(self.addDateButton)

        self.removeDateButton = QPushButton('Remove Date', self)
        self.removeDateButton.setVisible(False)  # Initially hide the remove button
        self.removeDateButton.clicked.connect(self.removeDateInput)
        dateButtonLayout.addWidget(self.removeDateButton)

        self.layout.addLayout(dateButtonLayout)
