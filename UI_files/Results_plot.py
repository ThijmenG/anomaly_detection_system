from PyQt5.QtWidgets import QSizePolicy, QMainWindow, QWidget, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, new_data, y_col):
        self.axes.clear()
        self.axes.plot(new_data.index, new_data[y_col])
        self.axes.set_title(f'Plot: {y_col}')
        self.draw()


class PlotWindow(QMainWindow):
    def __init__(self, new_data, predictions=None, clog_data=None):
        super().__init__()
        self.new_data = new_data
        self.predictions = predictions
        self.clog_data = clog_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Result')
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QVBoxLayout(self.centralWidget)

        self.yColumnComboBox = QComboBox(self)
        self.yColumnComboBox.addItems(self.new_data.columns)
        self.yColumnComboBox.currentIndexChanged.connect(self.updatePlot)
        layout.addWidget(self.yColumnComboBox)

        self.canvasLayout = QVBoxLayout()
        layout.addLayout(self.canvasLayout)

        self.canvas = PlotCanvas(self, width=5, height=4)
        self.canvasLayout.addWidget(self.canvas)
        self.updatePlot()

    def updatePlot(self):
        y_col = self.yColumnComboBox.currentText()
        self.canvas.plot(self.new_data, y_col)
