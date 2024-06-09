from PyQt5.QtWidgets import QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

class PlotCanvas(FigureCanvas):
    """ Class to create a plot canvas for the plot window."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, new_data, y_col, predictions=None, selected_prediction=None, clogs=None):
        try:
            self.axes.clear()

            # Ensure the 'Date' column is in datetime format and set as index
            if 'Date' not in new_data.columns:
                raise ValueError("The DataFrame must contain a 'Date' column.")

            # Convert 'Date' column to datetime
            new_data['Date'] = pd.to_datetime(new_data['Date'], errors='coerce')
            new_data = new_data.dropna(subset=['Date'])  # Drop rows where 'Date' could not be converted
            new_data.set_index('Date', inplace=True)

            # Drop any rows with NaT values in y_col
            new_data = new_data.dropna(subset=[y_col])

            # Plot the data
            self.axes.plot(new_data.index, new_data[y_col])
            self.axes.set_title(f'Plot: {y_col}')
            self.axes.set_xlabel('Date')
            self.axes.set_ylabel(y_col)

            # Add vertical lines for each datetime in predictions
            if predictions is not None:
                for prediction in predictions:
                    line_width = 2 if prediction == selected_prediction else 1
                    self.axes.axvline(x=prediction, color='r', linestyle='--', linewidth=line_width)

            # Add vertical lines for each datetime in clog_data
            if clogs is not None:
                clog_dates = clogs["Date"]
                for clog in clog_dates:
                    self.axes.axvline(x=clog, color='b', linestyle='-', linewidth=2)

            # Set x-axis ticks to show only 20 evenly spaced points
            x_ticks = np.linspace(0, len(new_data.index) - 1, 20, dtype=int)
            self.axes.set_xticks(new_data.index[x_ticks])
            self.axes.set_xticklabels(new_data.index[x_ticks].strftime('%Y-%m-%d %H:%M:%S'), rotation=45, ha='right')

            # Set y-axis limits and ticks
            y_min, y_max = new_data[y_col].min(), new_data[y_col].max()
            self.axes.set_ylim([y_min, y_max])
            self.axes.set_yticks(np.linspace(y_min, y_max, 10))

            self.draw()
        except Exception as e:
            print(f"Error in plot: {e}")


class PlotWindow(QMainWindow):
    """ Class to create a window for plotting the results."""
    def __init__(self, new_data, predictions=None, clog_data=None):
        super().__init__()
        self.new_data = new_data
        self.predictions = predictions
        self.clog_data = clog_data
        self.selected_prediction = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Result')
        self.setGeometry(100, 100, 1000, 600)  # Increase window width to accommodate the list

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        mainLayout = QHBoxLayout(self.centralWidget)  # Use horizontal layout for main layout

        # Create a layout for the predictions list
        self.predictionsLayout = QVBoxLayout()
        self.predictionsLabel = QLabel("Possible Clog Moments")
        self.predictionsList = QListWidget(self)

        if self.predictions is not None:
            for prediction in self.predictions:
                item = QListWidgetItem(prediction.strftime('%Y-%m-%d %H:%M:%S'))
                item.setData(Qt.UserRole, prediction)
                self.predictionsList.addItem(item)

        self.predictionsList.itemClicked.connect(self.onPredictionSelected)

        self.predictionsLayout.addWidget(self.predictionsLabel)
        self.predictionsLayout.addWidget(self.predictionsList)

        # Create a layout for the plot
        self.plotLayout = QVBoxLayout()
        self.yColumnComboBox = QComboBox(self)
        # List of columns to be included in the plot
        columns_to_plot = ['18BL02PT\\PV -  (Bar)', '18BL03PT\\PV -  (Bar)', '18FI02LT01 -  (kg)', '18OV01HM01_filtered -  (%)']

        # Filter the columns of new_data to include only the specified columns
        columns_in_data = [col for col in columns_to_plot if col in self.new_data.columns]

        # Add items to the combo box
        self.yColumnComboBox.addItems(columns_in_data)
        self.yColumnComboBox.currentIndexChanged.connect(self.updatePlot)
        self.plotLayout.addWidget(self.yColumnComboBox)

        self.canvas = PlotCanvas(self, width=5, height=4)
        self.plotLayout.addWidget(self.canvas)

        # plot toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolLayout = QVBoxLayout()
        self.toolLayout.addWidget(self.toolbar)
        self.plotLayout.addLayout(self.toolLayout)

        # Add the layouts to the main layout
        mainLayout.addLayout(self.predictionsLayout, 1)  # Give more space to the plot
        mainLayout.addLayout(self.plotLayout, 3)  # Give more space to the plot
        
        self.updatePlot()

    def updatePlot(self):
        y_col = self.yColumnComboBox.currentText()
        self.canvas.plot(self.new_data, y_col, self.predictions, self.selected_prediction, self.clog_data)

    def onPredictionSelected(self, item):
        self.selected_prediction = item.data(Qt.UserRole)
        self.updatePlot()
