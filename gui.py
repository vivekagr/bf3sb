import sys
import os
import random
import string
import webbrowser
from time import time
from socket import error as socker_error
from urllib2 import URLError
from tempfile import gettempdir
from PySide import QtGui, QtCore
from furl.furl import furl
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from bf3 import BF3Server, browse_server, get_regions
from iso_country_codes import COUNTRY
from pinger import do_one


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Battlefield 3 Server Browser')

        # Main Vertical Box Layout
        vbox = QtGui.QVBoxLayout()

        # Maps List
        self.map_check_box, map_widget = self.make_layout(2, BF3Server.map_code.values(), 'MAPS')

        # Mode List
        self.mode_check_box, mode_widget = self.make_layout(2, BF3Server.game_mode.values(), 'MODE')

        # Game Size List
        self.game_size_check_box, game_size_widget = self.make_layout(6, BF3Server.game_size.values(), 'GAME SIZE')

        # Free Slots List
        self.free_slots_check_box, free_slots_widget = self.make_layout(5, BF3Server.free_slots.values(), 'FREE SLOTS')

        # Preset List
        self.preset_check_box, preset_widget = self.make_layout(3, BF3Server.preset.values(), 'PRESET')

        # Base Game and Expansion Packs List
        self.game_check_box, game_widget = self.make_layout(3, BF3Server.game.values(), 'GAME')

        # Text box for server name search query
        self.server_name_search_box = QtGui.QLineEdit()
        self.server_name_search_box.setPlaceholderText("Server Name Filter")

        # Max results limit spinbox, its label and the QHboxLayout
        self.results_limit_spinbox = QtGui.QSpinBox()
        self.results_limit_spinbox.setRange(1, 1000)
        self.results_limit_spinbox.setValue(30)
        results_limit_label = QtGui.QLabel("Maximum number of results")
        results_limit_hbox = QtGui.QHBoxLayout()
        results_limit_hbox.addWidget(results_limit_label)
        results_limit_hbox.addSpacing(30)
        results_limit_hbox.addWidget(self.results_limit_spinbox)

        self.countries = []
        self.countries_full = []
        self.detailed_settings = {
            "premium": "-1",
            "ranked": "-1",
            "punkbuster": "-1",
            "mapRotation": "-1",
            "modeRotation": "-1",
            "password": "-1"
        }
        self.ping_repeat = 3
        self.ping_step = 5

        # Lets make the buttons
        self.browse_button = QtGui.QPushButton('Browse')
        default_button = QtGui.QPushButton('Default')
        regions_button = QtGui.QPushButton('Set Region')
        detailed_settings_button = QtGui.QPushButton('Settings')
        # QHBoxLayout for the buttons
        button_hbox = QtGui.QHBoxLayout()
        # Adding the buttons to the layout. addStretch() adds blank space between the buttons.
        button_hbox.addWidget(default_button)
        button_hbox.addStretch(True)
        button_hbox.addWidget(detailed_settings_button)
        button_hbox.addWidget(regions_button)
        button_hbox.addWidget(self.browse_button)

        # QVBoxLayout for adding various small widgets to the left.
        vbox_left = QtGui.QVBoxLayout()
        vbox_left.addWidget(mode_widget)
        vbox_left.addWidget(game_size_widget)
        vbox_left.addWidget(free_slots_widget)
        vbox_left.addWidget(preset_widget)
        vbox_left.addWidget(game_widget)

        # QVBoxLayout fir adding map name checkboxes and other widgets.
        vbox_right = QtGui.QVBoxLayout()
        vbox_right.addWidget(map_widget)
        vbox_right.addWidget(self.server_name_search_box)
        vbox_right.addLayout(results_limit_hbox)

        # QHBoxLayout for making two main columns. vbox_left is added to the left and map_widget to the right.
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        # Label to show the selected regions/countries.
        self.region_label = QtGui.QLabel("Region: None")
        self.region_label.setWordWrap(True)

        # Finally adding the hbox containing almost all checkboxes to the main vbox.
        # Buttons are added to the bottom of the vbox.
        vbox.addLayout(hbox)
        vbox.addWidget(self.region_label)
        vbox.addLayout(button_hbox)

        self.browse_button.clicked.connect(self.fetch_data)
        default_button.clicked.connect(self.set_default)
        regions_button.clicked.connect(self.call_region_window)
        detailed_settings_button.clicked.connect(self.call_settings_window)

        temp = QtGui.QWidget()
        temp.setLayout(vbox)
        self.setCentralWidget(temp)
        self.set_default()

    def make_layout(self, col, label_list, group_box_label):
        """
        Makes a QGridLayout of checkboxes based on the following parameters.
        :param col: Number of columns the grid should have.
        :param label_list: List of string values to use as label for the checkboxes.
        :param group_box_label: Label (string) to use for group box enclosing the grid.
        :return check_box_list: List of QCheckBox objects.
        :return group_box: QGroupBox object enclosing the grid of checkboxes.
        """
        check_box_list = []
        if len(label_list) < col:
            col = len(label_list)
        grid_layout = QtGui.QGridLayout()
        for i in range((len(label_list) / col) + 1):
            for j in range(col):
                index = (i * col) + j
                if index > len(label_list) - 1:
                    continue
                check_box_list.append(QtGui.QCheckBox(label_list[index]))
                grid_layout.addWidget(check_box_list[-1], i, j)
        group_box = QtGui.QGroupBox(group_box_label)
        group_box.setLayout(grid_layout)
        return check_box_list, group_box

    def set_default(self):
        """ Checks the default options as on Battlelog. """
        check_box_listception = (self.map_check_box, self.mode_check_box, self.game_size_check_box,
                                 self.free_slots_check_box, self.preset_check_box, self.game_check_box)
        self.clear_all_checkboxes(check_box_listception)
        map(lambda x: x.toggle(), self.game_check_box)
        self.preset_check_box[0].toggle()
        self.server_name_search_box.clear()
        self.results_limit_spinbox.setValue(30)

    def clear_all_checkboxes(self, check_box_listception):
        """ Clears all the checkboxes. """
        for check_box_list in check_box_listception:
            for check_box in check_box_list:
                if check_box.isChecked():
                    check_box.toggle()

    def fetch_data(self):
        """
        Fetches the data from Battlelog and shows the result to the user.
        Here self.build_url() is called for every QCheckBox list we have.
        Checks whether the application has admin privilege by sending one ping.
        """
        try:
            do_one("battlelog.battlefield.com")
        except socker_error:
            error_msg = "Cannot ping the servers since the application doesn't have admin privilege."
            QtGui.QMessageBox.warning(self, "Socket Error", error_msg)
            return
        self.browse_button.setText("Working...")
        self.base_url = furl("http://battlelog.battlefield.com/bf3/servers/")
        self.base_url.add({'filtered': '1'})
        self.build_url(self.map_check_box, BF3Server.map_code, 'maps')
        self.build_url(self.mode_check_box, BF3Server.game_mode, 'gamemodes')
        self.build_url(self.game_size_check_box, BF3Server.game_size, 'gameSize')
        self.build_url(self.free_slots_check_box, BF3Server.free_slots, 'slots')
        self.build_url(self.preset_check_box, BF3Server.preset, 'gamepresets')
        self.build_url(self.game_check_box, BF3Server.game, 'gameexpansions')
        self.base_url.add(self.detailed_settings)
        if self.countries:
            self.base_url.add({'useLocation': '1'})
            self.base_url.add({'country': '|'.join(self.countries)})
        if self.server_name_search_box.text():
            self.base_url.add({'q': self.server_name_search_box.text()})
        print self.base_url
        params = dict(url=str(self.base_url), limit=self.results_limit_spinbox.value(),
                      ping_repeat=self.ping_repeat, ping_step=self.ping_step)
        self.worker = WorkerThread(params)
        self.worker.start()
        self.browse_button.setDisabled(True)
        self.worker.network_error_signal.connect(self.show_network_error_message)
        self.worker.completed.connect(self.enable_browse_button)

    def build_url(self, check_box_list, bf3_data_list, param_name):
        """
        Checks every QCheckBox object in check_box_list for whether it is checked
        and builds URL query according to that.
        Doesn't returns anything. Just modifies the self.base_url
        """
        for checkbox in check_box_list:
            if checkbox.isChecked():
                map_name = [x for x, y in bf3_data_list.iteritems() if y == checkbox.text()]
                self.base_url.add({param_name: map_name})

    def show_network_error_message(self):
        error_msg = "Unable to retrieve server data from the Battlelog. Please check your network connection."
        QtGui.QMessageBox.warning(self, "Network Error", error_msg)

    def enable_browse_button(self):
        self.browse_button.setEnabled(True)
        self.browse_button.setText("Browse")

    def call_region_window(self):
        """
        Invokes the Region Selection dialog.
        """
        try:
            country_codes = get_regions()
        except URLError:
            error_message = "Unable to retrieve region data from the Battlelog. Please check your network connection."
            QtGui.QMessageBox.warning(self, "Network Error", error_message)
            return
        dialog = RegionDialog(country_codes, self.countries_full)
        if dialog.exec_():
            checked_countries = []
            for region in dialog.cc_check_boxes:
                for check_box in region:
                    if check_box.isChecked():
                        checked_countries.append(check_box.text())
            self.countries_full = checked_countries
            if len(checked_countries):
                region_label_text = "Regions: " + ', '.join(checked_countries)
                self.region_label.setText(region_label_text)
                self.countries = [y.lower() for x in checked_countries for y, z in COUNTRY.iteritems() if z == x.upper()]
            else:
                self.region_label.setText("Region: None")
                self.countries = []

    def call_settings_window(self):
        """
        Invokes the Settings dialog.
        """
        dialog = SettingsWindow(self.detailed_settings, self.ping_repeat, self.ping_step)
        if dialog.exec_():
            value = {'Yes': '1', 'No': '0', 'All': '-1'}
            for param_name, radio_buttons in dialog.radio_buttons.iteritems():
                for radio_btn in radio_buttons:
                    if radio_btn.isChecked():
                        self.detailed_settings[param_name] = value[radio_btn.text()]
            self.ping_repeat = dialog.ping_repeat.value()
            self.ping_step = dialog.ping_step.value()


class RegionDialog(QtGui.QDialog, MainWindow):

    def __init__(self, country_codes, countries, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('Region Selector')
        self.countries = countries
        vbox = QtGui.QVBoxLayout()

        self.cc_check_boxes = []
        cc_group_boxes = []
        for region in country_codes.keys():
            country_codes_list = [COUNTRY[i.upper()].title() for i in country_codes[region]]
            check_boxes, group_box = self.make_layout(2, country_codes_list, BF3Server.regions[region])
            self.cc_check_boxes.append(check_boxes)
            cc_group_boxes.append(group_box)

        hbox = QtGui.QHBoxLayout()
        hbox_vbox_left = QtGui.QVBoxLayout()
        hbox_vbox_right = QtGui.QVBoxLayout()

        hbox_vbox_left.addWidget(cc_group_boxes[0])
        hbox_vbox_left.addWidget(cc_group_boxes[-1])
        for i in cc_group_boxes[1:-1]:
            hbox_vbox_right.addWidget(i)

        hbox.addLayout(hbox_vbox_left)
        hbox.addLayout(hbox_vbox_right)
        vbox.addLayout(hbox)

        button_hbox = QtGui.QHBoxLayout()
        clear_all_button = QtGui.QPushButton("Clear All")
        ok_button = QtGui.QPushButton("OK")
        cancel_button = QtGui.QPushButton("Cancel")
        button_hbox.addWidget(clear_all_button)
        button_hbox.addStretch(True)
        button_hbox.addWidget(ok_button)
        button_hbox.addWidget(cancel_button)
        vbox.addLayout(button_hbox)

        clear_all_button.clicked.connect(self.clear_checkboxes)
        self.connect(ok_button, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))
        self.connect(cancel_button, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))

        self.check_already_selected_boxes()

        self.setLayout(vbox)
        self.setFixedSize(self.sizeHint())

    def clear_checkboxes(self):
        self.clear_all_checkboxes(self.cc_check_boxes)

    def check_already_selected_boxes(self):
        if self.countries:
            for check_boxes in self.cc_check_boxes:
                for check_box in check_boxes:
                    if check_box.text() in self.countries:
                        check_box.toggle()


class SettingsWindow(QtGui.QDialog):

    def __init__(self, detailed_settings, ping_repeat_val, ping_step_val, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.detailed_settings = detailed_settings
        self.ping_repeat_val = ping_repeat_val
        self.ping_step_val = ping_step_val

        vbox = QtGui.QVBoxLayout()

        premium, premium_radio_buttons = self.make_group_radio_buttons("Premium")
        ranked, ranked_radio_buttons = self.make_group_radio_buttons("Ranked")
        punkbuster, punkbuster_radio_buttons = self.make_group_radio_buttons("Punkbuster")
        map_rotation, map_rotation_radio_buttons = self.make_group_radio_buttons("Map Rotation")
        mode_rotation, mode_rotation_radio_buttons = self.make_group_radio_buttons("Game Mode Rotation")
        password_protection, password_protection_radio_buttons = self.make_group_radio_buttons("Password Protection")

        self.radio_buttons = {
            "premium": premium_radio_buttons,
            "ranked": ranked_radio_buttons,
            "punkbuster": punkbuster_radio_buttons,
            "mapRotation": map_rotation_radio_buttons,
            "modeRotation": mode_rotation_radio_buttons,
            "password": password_protection_radio_buttons
        }

        grid = QtGui.QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(premium, 0, 0)
        grid.addWidget(ranked, 0, 1)
        grid.addWidget(punkbuster, 0, 2)
        grid.addWidget(map_rotation, 1, 0)
        grid.addWidget(mode_rotation, 1, 1)
        grid.addWidget(password_protection, 1, 2)
        vbox.addLayout(grid)

        advanced_group_box = QtGui.QGroupBox("Advanced Settings")
        advanced_vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(QtGui.QLabel("Number of times to repeat ping process"))
        self.ping_repeat = QtGui.QSpinBox()
        self.ping_repeat.setRange(1, 100)
        self.ping_repeat.setValue(self.ping_repeat_val)
        hbox1.addWidget(self.ping_repeat)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(QtGui.QLabel("Number of servers to ping at a time"))
        self.ping_step = QtGui.QSpinBox()
        self.ping_step.setRange(1, 100)
        self.ping_step.setValue(self.ping_step_val)
        hbox2.addWidget(self.ping_step)
        advanced_vbox.addLayout(hbox1)
        advanced_vbox.addLayout(hbox2)
        advanced_group_box.setLayout(advanced_vbox)
        vbox.addWidget(advanced_group_box)

        button_hbox = QtGui.QHBoxLayout()
        ok_button = QtGui.QPushButton("OK")
        cancel_button = QtGui.QPushButton("Cancel")
        button_hbox.addStretch(True)
        button_hbox.addWidget(ok_button)
        button_hbox.addWidget(cancel_button)
        vbox.addLayout(button_hbox)

        self.connect(ok_button, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))
        self.connect(cancel_button, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))

        self.check_already_selected_boxes()

        self.setLayout(vbox)
        self.setFixedSize(self.sizeHint())

    def make_group_radio_buttons(self, title):
        group_box = QtGui.QGroupBox(title)
        hbox = QtGui.QHBoxLayout()
        true_radio_button = QtGui.QRadioButton("Yes")
        false_radio_button = QtGui.QRadioButton("No")
        none_radio_button = QtGui.QRadioButton("All")
        none_radio_button.setChecked(True)
        hbox.addWidget(true_radio_button)
        hbox.addWidget(false_radio_button)
        hbox.addWidget(none_radio_button)
        group_box.setLayout(hbox)
        radio_buttons = (true_radio_button, false_radio_button, none_radio_button)
        return group_box, radio_buttons

    def check_already_selected_boxes(self):
        if self.detailed_settings:
            value_dict = {'1': 'Yes', '0': 'No', '-1': 'All'}
            for param_name, value in self.detailed_settings.iteritems():
                for radio_button in self.radio_buttons[param_name]:
                    if value_dict[value] == radio_button.text():
                        radio_button.setChecked(True)


class WorkerThread(QtCore.QThread):

    network_error_signal = QtCore.Signal()
    completed = QtCore.Signal()

    def __init__(self, params, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.params = params

    def run(self):
        start_time = time()
        try:
            server_list = browse_server(**self.params)
        except URLError:
            self.network_error_signal.emit()
        else:
            time_elapsed = round(time() - start_time, 2)
            template_env = Environment()
            template_env.loader = FileSystemLoader('.')
            template_args = dict(servers=enumerate(server_list), bf3=BF3Server, time_elapsed=time_elapsed)
            output = template_env.get_template('layout.html').render(**template_args).encode('utf8')
            temp_storage_dir = gettempdir() + '\\bf3sb'
            if not os.access(temp_storage_dir, os.F_OK):
                os.mkdir(temp_storage_dir)
            random_file_name = ''.join(random.sample(string.lowercase + string.digits, 20)) + '.html'
            random_file_path = temp_storage_dir + '\\' + random_file_name
            f = open(random_file_path, 'w')
            f.write(output)
            f.close()
            webbrowser.open(random_file_path)
        finally:
            self.completed.emit()

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
window.setFixedSize(window.size())
app.exec_()
