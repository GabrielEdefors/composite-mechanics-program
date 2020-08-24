import matplotlib
import os
import abc

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from composite import plot_tools_GUI, LoadType
from coordinate_systems import CoordinateSystem
from model import Quantity, ResultData

matplotlib.use('Qt5Agg')
# -*- coding: utf-8 -*-


class MainWindow(QMainWindow):
    """The main window of the GUI

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model

    """
    def __init__(self, model):

        super().__init__()
        self.model = model
        self.directory = os.path.dirname(os.path.realpath(__file__))

        # Set window properties
        self.setWindowTitle('Composite Calculator 2000')
        self.setWindowIcon(QIcon(self.directory + os.path.sep + 'icon.png'))
        self.resize(700, 650)

        # Create a group box view holding all sub widgets
        self.view = View(model, self)
        self.setCentralWidget(self.view)

        # Add menu bar with file and Export options
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.export_menu = self.menu_bar.addMenu('Export')

        # Actions for file menu
        quit_action = QAction('Quit', self)
        self.file_menu.addAction(quit_action)

        # Actions for Export menu
        export_textfile_action = QAction('Numerical Results', self)
        self.export_menu.addAction(export_textfile_action)

        # Controllers for the menu bar buttons
        def export_textfile():
            # Open a new window containing export options
            self.export_textfile_window = ExportTextFileWindow(self.model, self, "Export Numerical Results",
                                                               "Select Which Results to Export",
                                                               "Results Due to Thermal Loading",
                                                               "Results Due to Combined Loading")
            self.export_textfile_window.show()
        export_textfile_action.triggered.connect(export_textfile)

        quit_action.triggered.connect(self.close)


class View(QGroupBox):
    """The main group box holding all subgroups

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QMainWindow

    """

    def __init__(self, model, parent):
        super().__init__()

        self.model = model
        self.parent = parent

        # Create subgroups for canvas and input and calculation options
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

    def reset_GUI(self):
        """Resets all problem specific data"""

        self.canvas_group.plot_properties.reset_load_types()
        self.canvas_group.canvas.reset_axes()

class CanvasGroup(QGroupBox):
    """ Group box containing canvas object and plot properties group box

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGRoupBox

    """

    def __init__(self, model, parent):
        super().__init__("Result Display")

        self.model = model
        self.parent = parent

        # Connect logic from model
        self.model.plot_display_data.connect(self.plot_data)

        # Create canvas instance and Properties grop box instance
        self.canvas = Canvas(self)
        self.plot_properties = PlotPropertiesGroup(self.model, self)

        # Add the properties box and canvas
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.plot_properties)
        self.layout.addWidget(self.canvas)

        # Horizontal layout beneath the canvas
        self.save_button = QPushButton('Save Image')
        self.grid_option_box = QComboBox(self)
        self.grid_option_box.addItem('Grid Off')
        self.grid_option_box.addItem('Grid On')
        self.bottom_horizontal_layout = QHBoxLayout()
        self.bottom_horizontal_layout.addWidget(self.grid_option_box)
        self.bottom_horizontal_layout.addWidget(self.save_button)
        self.bottom_horizontal_layout.addStretch()

        # Add the the bottom layout to the main layout
        self.layout.addLayout(self.bottom_horizontal_layout)
        self.setLayout(self.layout)

        # Finally dray the canvas
        self.canvas.draw()

        # Controllers for save button and grid combo box
        def export_imagefile():

            filepath, filetype = QFileDialog.getSaveFileName(self, 'Save As', self.parent.parent.directory,
                                                             "Image Files (*.png *.jpg *.svg)")
            self.canvas.figure.savefig(filepath)
        self.save_button.clicked.connect(export_imagefile)

        def change_grid_settings():
            if self.grid_option_box.currentText() == 'Grid On':
                self.plot_data(grid=True)
            else:
                self.plot_data(grid=False)
        self.grid_option_box.activated.connect(change_grid_settings)

    def plot_data(self, grid=False):

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

        self.canvas.graph = plot_tools_GUI.plot_stress(axes=canvas_axes, coordinates=self.model.z_coordinates, quantity=array_to_plot, component=self.model.display_component)
        self.canvas.figure.tight_layout(w_pad=1)
        self.canvas.axes.grid(grid)
        self.canvas.draw()


class PlotPropertiesGroup(QGroupBox):
    """ Group box containing plot properties

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGroupBox

    """

    def __init__(self, model, parent):
        super().__init__()

        self.model = model
        self.parent = parent

        # Hide box boundaries
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

        # Add drop down menu for choosing tensor components
        self.combo_box_component = QComboBox(self)
        self.combo_box_component.addItem("\u03C3\u2081")
        self.combo_box_component.addItem("\u03C3\u2082")
        self.combo_box_component.addItem("\u03C3\u2083")
        self.combo_box_component.addItem("\u03B5\u2081")
        self.combo_box_component.addItem("\u03B5\u2082")
        self.combo_box_component.addItem("\u03B5\u2083")
        self.horizontal_layout.addWidget(self.combo_box_component)
        self.horizontal_layout.addStretch()

        self.setLayout(self.horizontal_layout)

        # Controllers for buttons and combo boxes
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

            # Redraw canvas
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
        """Adds items to the load type combo box based on available results

            :param load_type: Load type to be added
            :type load_type: LoadType Enum

        """

        if load_type == LoadType.thermal:
            self.combo_box_loadtype.addItem("Thermal")
        else:
            self.combo_box_loadtype.addItem("Combined")

    def reset_load_types(self):
        """Removes all but first Item of the combo box"""

        while self.combo_box_loadtype.count() > 1:
            self.combo_box_loadtype.removeItem(self.combo_box_loadtype.count()-1)

class InputGroup(QGroupBox):
    """ Group box containing input options widgets

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGroupBox

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

        # Controllers for input file button and project name line edit
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
        """Updates the text displayed in the project name line edit

            param new_text: Text to be displayed
            type new_text: str

        """
        self.input_project_name.setPlaceholderText(new_text)

    def delete_text(self):
        """Deletes the text displayed in the project name line edit
        """
        self.input_project_name.setText("")


class CalculateGroup(QGroupBox):
    """ Group box containing calculation options

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGroupBox
    """

    def __init__(self, model, parent):
        super().__init__("Calculate")

        self.model = model
        self.parent = parent

        self.layout = QVBoxLayout()

        # Add check boxes for choosing what to calculate
        self.check_box_thermal = QCheckBox("Calculate Results Due to Thermal Loading")
        self.check_box_total = QCheckBox("Calculate Results Due to Combined Loading")
        self.calculate_button = QPushButton("Calculate")
        self.layout.addWidget(self.check_box_thermal)
        self.layout.addWidget(self.check_box_total)
        self.layout.addWidget(self.calculate_button)

        # Add the widgets to the top of the group box
        self.setLayout(self.layout)
        self.layout.addStretch(1)

        # Controllers for calculation button
        def calculate():

            # Reset GUI
            self.parent.reset_GUI()

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


class Canvas(FigureCanvasQTAgg):
    """ Canvas that hold the stress and strain plots

        :param parent: The parent widget of the group box
        :type parent: QGroupBox

    """

    def __init__(self, parent):
        self.parent = parent

        # Create a figure and populate with a subplot
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        super(Canvas, self).__init__(self.figure)

    def reset_axes(self):
        """Clears the content of the axes"""
        self.axes.clear()

    def set_axis_title(self, load_type, quantity, component):
        """Sets the title of the axes based on load type, quatity and component

            :param load_type: Load type plotted
            :type load_type: LoadType
            :param quantity: Quantity plotted (stress or strain)
            :type quantity: Quantity
            :param component: Component plotted
            :type component: int

        """
        title = load_type.name.capitalize() + ' ' + quantity.name + ', component ' + str(component + 1)
        self.axes.set_title(title)


class ExportFileWindow(QMainWindow):
    """ A general export window containing check boxes and a button

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGroupBox
        :param title: Title of the window
        :param label: String to be displayed in the label above the check boxes
        :param checkbox_1: String to be displayed in the upper check box
        :param checkbox_2: String to be displayed in the lower check box

    """

    def __init__(self, model, parent, title, label, checkbox_1, checkbox_2):
        super().__init__()
        self.model = model
        self.parent = parent
        self.title = title

        # Set window properties
        self.setWindowTitle(self.title)
        self.resize(300, 200)
        self.layout = QVBoxLayout()
        self.group_box = QGroupBox("Export Options")
        self.layout.addWidget(self.group_box)
        self.setLayout(self.layout)

        # Add check boxes for choosing load types to export
        self.load_type_label = QLabel(label)
        self.check_box_1 = QCheckBox(checkbox_1)
        self.check_box_2 = QCheckBox(checkbox_2)
        self.group_box.layout = QVBoxLayout()
        self.group_box.layout.addWidget(self.load_type_label)
        self.group_box.layout.addWidget(self.check_box_1)
        self.group_box.layout.addWidget(self.check_box_2)
        self.group_box.layout.addStretch()

        # Disable check boxes based on available results
        self.disable_checkboxes()

        # Save button
        self.save_as_button = QPushButton("Save As")
        self.group_box.layout.addWidget(self.save_as_button)

        self.group_box.setLayout(self.group_box.layout)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        @abc.abstractmethod
        def save_as():
            """"Should implement choosing file and performing export"""""

    @abc.abstractmethod
    def disable_checkboxes(self):
        """should disable checkboxes based on availability of results"""
        pass

    @staticmethod
    def no_selection_inform():
        """Displays a message box informing that no selection has been made"""
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message = "No selection made, nothing exported"
        message_box.setText(message)
        message_box.exec_()


class ExportTextFileWindow(ExportFileWindow):
    """Window for exporting text files of the results

        :param model: Class containing all the logic of the GUI
        :type model: Instance of Model
        :param parent: The parent widget of the group box
        :type parent: QGroupBox
        :param title: Title of the window
        :param label: String to be displayed in the label above the check boxes
        :param checkbox_1: String to be displayed in the upper check box
        :param checkbox_2: String to be displayed in the lower check box

    """

    def __init__(self, model, parent, title, label, checkbox_1, checkbox_2):
        super().__init__(model, parent, title, label, checkbox_1, checkbox_2)
        self.model = model
        self.parent = parent

        # Controller for the save as button
        def save_as():
            self.filepath, self.filetype = QFileDialog.getSaveFileName(self, 'Save As', self.parent.directory,
                                                           "Text Files (*.txt)")

            if self.check_box_1.isChecked() and self.check_box_2.isChecked():
                self.model.export_text_file(self.filepath, include_thermal=True, include_total=True)
                self.close()
            elif self.check_box_1.isChecked() and not self.check_box_2.isChecked():
                self.model.export_text_file(self.filepath, include_thermal=True)
                self.close()
            elif not self.check_box_1.isChecked() and self.check_box_2.isChecked():
                self.model.export_text_file(self.filepath, include_total=True)
                self.close()
            else:
                self.no_selection_inform()
        self.save_as_button.clicked.connect(save_as)

    # Implementation of disabling checkboxes
    def disable_checkboxes(self):
        """Disables load type if no results exist"""

        if not isinstance(self.model.result_thermal, ResultData):
            self.check_box_1.setEnabled(False)
        if not isinstance(self.model.result_total, ResultData):
            self.check_box_2.setEnabled(False)






