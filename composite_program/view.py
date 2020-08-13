from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from model import Quantity, ResultData
from coordinate_systems import CoordinateSystem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from composite import plot_tools_GUI, LoadType, print_tools

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
        self.resize(700, 650)
        self.setWindowIcon(QIcon(self.directory + os.path.sep + 'icon.png'))

        # View box
        self.view = View(model, self)
        self.setCentralWidget(self.view)

        # Add menu bar with file and Export options
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.export_menu = self.menu_bar.addMenu('Export')

        # Actions for file menu
        quit_action = QAction('Quit', self)
        self.file_menu.addAction(quit_action)

        # Actions for Currency menu
        export_textfile_action = QAction('Numerical Results', self)
        export_graph_action = QAction('Graphs', self)
        self.export_menu.addAction(export_textfile_action)
        self.export_menu.addAction(export_graph_action)

        # Connect menu bar buttons
        def export_textfile():
            # Open a new window containing export options
            self.export_textfile_window = ExportTextFileWindow(self.model, self)
            self.export_textfile_window.show()

        export_textfile_action.triggered.connect(export_textfile)


class View(QGroupBox):
    """ The main window of the GUI
    """

    def __init__(self, model, parent):
        super().__init__()

        self.model = model
        self.parent = parent

        # Create subgroups
        self.canvas_group = CanvasGroup(self.model, self)
        self.input_group = InputGroup(self.model, self)
        self.calculate_group = CalculateGroup(self.model, self)

        # Create main layout of the window and add subgroups
        self.main_layout = QHBoxLayout()
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.addWidget(self.input_group)
        self.left_panel_layout.addWidget(self.calculate_group)
        self.main_layout.addLayout(self.left_panel_layout)
        self.main_layout.addWidget(self.canvas_group)
        self.setLayout(self.main_layout)


class CanvasGroup(QGroupBox):
    """ Group box containing plot and plot properties

    """

    def __init__(self, model, parent):
        super().__init__("Result Display")

        self.model = model
        self.parent = parent

        # Connect logic
        self.model.plot_display_data.connect(self.plot_data)

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

    def plot_data(self):

        # Empty canvas axis
        self.canvas.reset_axes()

        canvas_axes = self.canvas.axes

        # Retrieve the data from the display_quantity
        quantity = self.model.display_quantity
        coordinates = self.model.display_coordinates

        if quantity == Quantity.stress and coordinates == CoordinateSystem.LT:
            array_to_plot = self.model.display_load_type.local_stress
            self.canvas.set_axis_title(self.model.display_load_type.local_stress.stress_type, quantity, self.model.display_component)
        elif quantity == Quantity.stress and coordinates == CoordinateSystem.xy:
            array_to_plot = self.model.display_load_type.global_stress
            self.canvas.set_axis_title(self.model.display_load_type.global_stress.stress_type, quantity, self.model.display_component)
        elif quantity == Quantity.strain and coordinates == CoordinateSystem.LT:
            array_to_plot = self.model.display_load_type.local_strains
            self.canvas.set_axis_title(self.model.display_load_type.local_strains.strain_type, quantity, self.model.display_component)
        else:
            array_to_plot = self.model.display_load_type.global_strains
            self.canvas.set_axis_title(self.model.display_load_type.local_strains.strain_type, quantity, self.model.display_component)

        plot_tools_GUI.plot_stress(axes=canvas_axes, coordinates=self.model.z_coordinates, quantity=array_to_plot, component=self.model.display_component)
        self.canvas.figure.tight_layout(w_pad=1)
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
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.local_button)
        self.horizontal_layout.addWidget(self.global_button)

        # Add drop down for choosing between thermal and total results
        self.combo_box_loadtype = QComboBox(self)
        self.combo_box_loadtype.addItem("Select Load Case")
        self.horizontal_layout.addWidget(self.combo_box_loadtype)

        # Add drop down menu for tensor components
        self.combo_box_component = QComboBox(self)
        self.combo_box_component.addItem("\u03C3\u2081")
        self.combo_box_component.addItem("\u03C3\u2082")
        self.combo_box_component.addItem("\u03C3\u2083")
        self.combo_box_component.addItem("\u03B5\u2081")
        self.combo_box_component.addItem("\u03B5\u2082")
        self.combo_box_component.addItem("\u03B5\u2083")
        self.horizontal_layout.addWidget(self.combo_box_component)

        self.setLayout(self.horizontal_layout)

        # Controllers
        def change_component():

            if self.combo_box_component.currentText() == "\u03C3\u2081":
                self.model.set_display_component(0)
                self.model.set_display_quantity(Quantity.stress)
            elif self.combo_box_component.currentText() == "\u03C3\u2082":
                self.model.set_display_component(1)
                self.model.set_display_quantity(Quantity.stress)
            elif self.combo_box_component.currentText() == "\u03C3\u2083":
                self.model.set_display_component(2)
                self.model.set_display_quantity(Quantity.stress)
            elif self.combo_box_component.currentText() == "\u03B5\u2081":
                self.model.set_display_component(0)
                self.model.set_display_quantity(Quantity.strain)
            elif self.combo_box_component.currentText() == "\u03B5\u2082":
                self.model.set_display_component(1)
                self.model.set_display_quantity(Quantity.strain)
            elif self.combo_box_component.currentText() == "\u03B5\u2083":
                self.model.set_display_component(2)
                self.model.set_display_quantity(Quantity.strain)

            # Redraw canvass
            self.parent.parent.canvas_group.plot_data()

        self.combo_box_component.currentIndexChanged.connect(change_component)

        def change_loadtype():

            if self.combo_box_loadtype.currentText() == 'Thermal':
                self.model.set_display_loadtype(LoadType.thermal)
            elif self.combo_box_loadtype.currentText() == 'Combined':
                self.model.set_display_loadtype(LoadType.combined)

            # Redraw canvas
            self.parent.parent.canvas_group.plot_data()
        self.combo_box_loadtype.currentIndexChanged.connect(change_loadtype)

        def display_local_coordinates():
            self.model.set_display_coordinates(CoordinateSystem.LT)

            # Redraw canvas
            self.parent.parent.canvas_group.plot_data()

        self.local_button.clicked.connect(display_local_coordinates)

        def display_global_coordinates():
            self.model.set_display_coordinates(CoordinateSystem.xy)

            # Redraw canvas
            self.parent.parent.canvas_group.plot_data()

        self.global_button.clicked.connect(display_global_coordinates)

    def add_load_types(self, load_type: LoadType):

        if load_type == LoadType.thermal:
            self.combo_box_loadtype.addItem("Thermal")
        else:
            self.combo_box_loadtype.addItem("Combined")


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

        self.check_box_thermal = QCheckBox("Calculate Results Due to Thermal Loading")
        self.check_box_total = QCheckBox("Calculate Results Due to Combined Loading")
        self.calculate_button = QPushButton("Calculate")
        self.layout.addWidget(self.check_box_thermal)
        self.layout.addWidget(self.check_box_total)
        self.layout.addWidget(self.calculate_button)

        self.setLayout(self.layout)
        self.layout.addStretch(1)

        # Controllers
        def calculate():
            calculate_thermal = False
            calculate_total = False
            if self.check_box_thermal.isChecked() is True:
                calculate_thermal = True
                self.parent.canvas_group.plot_properties.add_load_types(LoadType.thermal)
            if self.check_box_total.isChecked() is True:
                calculate_total = True
                self.parent.canvas_group.plot_properties.add_load_types(LoadType.combined)
            self.model.calculate(calculate_thermal, calculate_total)
        self.calculate_button.clicked.connect(calculate)

        # def calculate_total_stress():
        # self.model.calculate_total_stress()
        # self.calculate_total_button.clicked.connect(calculate_total_stress)


class Canvas(FigureCanvasQTAgg):
    """ Canvas that hold the stress and strain plots
    """

    def __init__(self, parent):
        self.parent = parent
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        super(Canvas, self).__init__(self.figure)

    def reset_axes(self):
        self.axes.clear()

    def set_axis_title(self, load_type, quantity, component):
        title = load_type.name.capitalize() + ' ' + quantity.name + ', component ' + str(component + 1)
        self.axes.set_title(title)


class ExportTextFileWindow(QMainWindow):
    def __init__(self, model, parent):
        super().__init__()
        self.model = model
        self.parent = parent

        # Set window properties
        self.setWindowTitle('Export Options')
        self.resize(300, 200)
        self.layout = QVBoxLayout()

        # Add check boxes for choosing load types to export
        self.load_type_label = QLabel("Select Which Results to export")
        self.check_box_thermal = QCheckBox("Results Due to Thermal Loading")
        self.check_box_total = QCheckBox("Results Due to Combined Loading")
        self.layout.addWidget(self.load_type_label)
        self.layout.addWidget(self.check_box_thermal)
        self.layout.addWidget(self.check_box_total)

        # Disable load type if not calculated
        if not isinstance(self.model.result_thermal, ResultData):
            self.check_box_thermal.setEnabled(False)
        if not isinstance(self.model.result_total, ResultData):
            self.check_box_total.setEnabled(False)

        # Save button
        self.save_as_button = QPushButton("Save As")
        self.layout.addWidget(self.save_as_button)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Controllers
        def save_as():
            self.filepath, self.filetype = QFileDialog.getSaveFileName(self, 'Save As', self.parent.directory,
                                                           "Text Files (*.txt)")

            self.model.export_text_file(self.filepath)

        self.save_as_button.clicked.connect(save_as)









