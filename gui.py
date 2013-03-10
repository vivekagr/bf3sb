import sys
import webbrowser
from PySide import QtGui, QtCore
from furl.furl import furl
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from time import time
from bf3 import BF3Server, browse_server


class MainWindow(QtGui.QDialog):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('BF3 Server Browser')
        self.setWindowFlags(QtGui.QStyle.SP_TitleBarMinButton)
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

        # Lets make the buttons
        browse_button = QtGui.QPushButton('Browse')
        default_button = QtGui.QPushButton('Default')
        # QHBoxLayout for the buttons
        button_hbox = QtGui.QHBoxLayout()
        # Adding the buttons to the layout. addStretch() adds blank space between the buttons.
        button_hbox.addWidget(default_button)
        button_hbox.addStretch(1)
        button_hbox.addWidget(browse_button)

        # QVBoxLayout for adding various small widgets.
        vbox_inner = QtGui.QVBoxLayout()
        vbox_inner.addWidget(mode_widget)
        vbox_inner.addWidget(game_size_widget)
        vbox_inner.addWidget(free_slots_widget)
        vbox_inner.addWidget(preset_widget)
        vbox_inner.addWidget(game_widget)

        # QHBoxLayout for making two main columns. vbox_inner is added to the left and map_widget to the right.
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox_inner)
        hbox.addWidget(map_widget)

        # Finally adding the hbox containing almost all checkboxes to the main vbox.
        # Buttons are added to the bottom of the vbox.
        vbox.addLayout(hbox)
        vbox.addLayout(button_hbox)

        browse_button.clicked.connect(self.fetch_data)
        default_button.clicked.connect(self.set_default)

        self.setLayout(vbox)
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
        self.clear_all_checkboxes()
        map(lambda x: x.toggle(), self.game_check_box)
        self.preset_check_box[0].toggle()

    def clear_all_checkboxes(self):
        """ Clears all the checkboxes. """
        check_box_listception = (self.map_check_box, self.mode_check_box, self.game_size_check_box,
                                 self.free_slots_check_box, self.preset_check_box, self.game_check_box)
        for check_box_list in check_box_listception:
            for check_box in check_box_list:
                if check_box.isChecked():
                    check_box.toggle()

    def fetch_data(self):
        """
        Fetches the data from Battlelog and shows the result to the user.
        Here self.build_url() is called for every QCheckBox list we have.
        """
        start_time = time()
        self.base_url = furl("http://battlelog.battlefield.com/bf3/servers/")
        self.base_url.add({'filtered': '1'})
        self.build_url(self.map_check_box, BF3Server.map_code, 'maps')
        self.build_url(self.mode_check_box, BF3Server.game_mode, 'gamemodes')
        self.build_url(self.game_size_check_box, BF3Server.game_size, 'gameSize')
        self.build_url(self.free_slots_check_box, BF3Server.free_slots, 'slots')
        self.build_url(self.preset_check_box, BF3Server.preset, 'gamepresets')
        self.build_url(self.game_check_box, BF3Server.game, 'gameexpansions')
        print self.base_url
        server_list = browse_server(url=str(self.base_url))
        time_elapsed = round(time() - start_time, 2)
        template_env = Environment()
        template_env.loader = FileSystemLoader('.')
        template_args = dict(servers=enumerate(server_list), bf3=BF3Server, time_elapsed=time_elapsed)
        output = template_env.get_template('layout.html').render(**template_args).encode('utf8')
        open('output_temp.html', 'w').write(output)
        webbrowser.open('output_temp.html')

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


app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
window.setFixedSize(window.size())
app.exec_()