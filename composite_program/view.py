from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
from model import DispCoordinates, Quantity

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from composite import plot_tools_GUI

import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.use('Qt5Agg')
# -*- coding: utf-8 -*-


class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.directory = os.path.dirname(os.path.realpath(__file__))

        # Set window properties
        self.setWindowTitle('Composite Calculator 2000')
        self.resize(800, 700)
        self.setWindowIcon(QIcon(self.directory + os.path.sep + 'icon.png'))

        # View box
        self.view = View(model, self)
        self.setCentralWidget(self.view)

        # Add menu bar with file and currency
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.currency_menu = self.menu_bar.addMenu('Currency')

        # Actions for file menu
        quit_action = QAction('Quit', self)
        self.file_menu.addAction(quit_action)

        # Actions for Currency menu
        SEK_currency_action = QAction('SEK', self)
        self.currency_menu.addAction(SEK_currency_action)

        # Connect menu bar buttons


class View(QGroupBox):
    """ The main window of the GUI
    """

    def __init__(self, model, parent):
        super().__init__()

        self.model = model
        self.parent = parent

        # Create subgroups
        self.button_group = CanvasGroup(self.model, self)
        self.input_group = InputGroup(self.model, self)
        self.calulate_group = CalculateGroup(self.model, self)

        # Create main layout of the window and add subgroups
        self.main_layout = QHBoxLayout()
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.addWidget(self.input_group)
        self.left_panel_layout.addWidget(self.calulate_group)
        self.main_layout.addLayout(self.left_panel_layout)
        self.main_layout.addWidget(self.button_group)
        self.setLayout(self.main_layout)


class CanvasGroup(QGroupBox):
    """ Group box containing plot and plot properties

    """

    def __init__(self, model, parent):
        super().__init__("Result Display")

        self.model = model
        self.parent = parent

        # Connect logic
        self.model.plot_data.connect(self.plot_data)

        # Contents
        self.layout = QVBoxLayout()
        self.canvas = Canvas(self)
        self.plot_properties = PlotPropertiesGroup(self.model, self)

        # Add the properties box and canvas
        self.layout.addWidget(self.plot_properties)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.canvas.draw()

        # Controllers

    def plot_data(self, z_coordinates, quantity, component):

        # Empty canvas axis
        self.canvas.reset_axes()

        canvas_axes = self.canvas.axes
        plot_tools_GUI.plot_stress(axes=canvas_axes, coordinates=z_coordinates, quantity=quantity, component=component)
        self.canvas.draw()


class PlotPropertiesGroup(QGroupBox):
    """ Group box containing plot properties

    """

    def __init__(self, model, parent):
        super().__init__()

        self.model = model
        self.parent = parent

        self.setFlat(True)

        # Add buttons
        self.local_button = QPushButton("Display In Local Coordinates")
        self.global_button = QPushButton("Display In Global Coordinates")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.local_button)
        self.layout.addWidget(self.global_button)


        # Add dropdown menu
        self.combo_box = QComboBox(self)
        self.combo_box.addItem("\u03C3\u2081")
        self.combo_box.addItem("\u03C3\u2082")
        self.combo_box.addItem("\u03C3\u2083")
        self.combo_box.addItem("\u03B5\u2081")
        self.combo_box.addItem("\u03B5\u2082")
        self.combo_box.addItem("\u03B5\u2083")
        self.layout.addWidget(self.combo_box)

        self.setLayout(self.layout)

        # Controllers
        def change_component():

            if self.combo_box.currentText() == "\u03C3\u2081":
                self.model.change_plot_component(Quantity.stress, 0)
            elif self.combo_box.currentText() == "\u03C3\u2082":
                self.model.change_plot_component(Quantity.stress, 1)
            elif self.combo_box.currentText() == "\u03C3\u2083":
                self.model.change_plot_component(Quantity.stress, 2)
            elif self.combo_box.currentText() == "\u03B5\u2081":
                self.model.change_plot_component(Quantity.strain, 0)
            elif self.combo_box.currentText() == "\u03B5\u2082":
                self.model.change_plot_component(Quantity.strain, 1)
            elif self.combo_box.currentText() == "\u03B5\u2083":
                self.model.change_plot_component(Quantity.strain, 2)
        self.combo_box.currentIndexChanged.connect(change_component)

        def display_local_coordinates():
            self.model.set_display_coordinates(DispCoordinates.local_system)
        self.local_button.clicked.connect(display_local_coordinates)

        def display_global_coordinates():
            self.model.set_display_coordinates(DispCoordinates.global_system)
        self.local_button.clicked.connect(display_global_coordinates)


class InputGroup(QGroupBox):
    """ Group box containing input text boxes
    """

    def __init__(self, model, parent):
        super().__init__("Inputs")

        self.model = model
        self.parent = parent
        self.filename = ""

        # Button layout
        self.buttons_layout = QVBoxLayout()
        self.input_file_button = QPushButton("Select Input File")
        self.buttons_layout.addWidget(self.input_file_button)
        #self.setLayout(self.buttons_layout)

        # Line edit layout
        self.line_edit_layout = QFormLayout()
        self.input_project_name = QLineEdit(placeholderText="")
        self.input_project_name.setFixedWidth(120)
        self.line_edit_layout.addRow("Project Name", self.input_project_name)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addLayout(self.line_edit_layout)
        self.setLayout(self.main_layout)


        # Controllers
        def select_file():

            # Prompt for filepath
            filepath, _ = QFileDialog.getOpenFileName(self.parent, 'Select Input File', self.parent.parent.directory, "Input files (*.txt)")

            # Update the placeholder for the project name text
            self.filename = filepath.split('/')[-1].replace('.txt', '')
            self.update_placeholder_text(self.filename)

            # Update model
            self.model.set_input_directory(filepath)
            self.model.set_project_name(self.filename)
            self.model.read_input_file()

        self.input_file_button.clicked.connect(select_file)

        def update_project_name():

            self.filename = self.input_project_name.text()

            # Update model
            self.model.set_project_name(self.filename)
            self.update_placeholder_text(self.filename)

            # Set new placeholder
            self.update_placeholder_text(self.filename)
            self.delete_text()

        self.input_project_name.returnPressed.connect(update_project_name)


    def update_placeholder_text(self, new_text):
        self.input_project_name.setPlaceholderText(new_text)

    def delete_text(self):
        self.input_project_name.setText("")


class CalculateGroup(QGroupBox):
    """ Group box containing calculation options
    """

    def __init__(self, model, parent):
        super().__init__("Calculate")

        self.model = model
        self.parent = parent

        self.layout = QVBoxLayout()
        self.calculate_thermal_button = QPushButton("Calculate Thermal Stress")
        self.calculate_total_button = QPushButton("Calculate Total Stress")
        self.layout.addWidget(self.calculate_thermal_button)
        self.layout.addWidget(self.calculate_total_button)
        self.setLayout(self.layout)
        self.layout.addStretch(1)

        # Controllers
        def calculate_thermal_stress():
            self.model.calculate_thermal_stress()
        self.calculate_thermal_button.clicked.connect(calculate_thermal_stress)


class Canvas(FigureCanvasQTAgg):
    """ Canvas that hold the stress and strain plots
    """

    def __init__(self, parent):
        self.parent = parent
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        plt.tight_layout()
        super(Canvas, self).__init__(self.figure)

    def reset_axes(self):
        self.axes.clear()







