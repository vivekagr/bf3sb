from PySide import QtGui, QtCore
from bf3 import BF3Server
import sys


class MainWindow(QtGui.QDialog):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('BF3 Server Pinger')
        self.setWindowFlags(QtGui.QStyle.SP_TitleBarMinButton)
        # Main Vertical Box Layout
        vbox = QtGui.QVBoxLayout()

        # Maps List
        map_check_box, map_widget = self.make_layout(2, BF3Server.map_code.values(), 'MAPS')

        # Mode List
        mode_check_box, mode_widget = self.make_layout(2, BF3Server.game_mode.values(), 'MODE')

        # Game Size List
        game_size_check_box, game_size_widget = self.make_layout(6, BF3Server.game_size.values(), 'GAME SIZE')

        # Free Slots List
        free_slots_check_box, free_slots_widget = self.make_layout(5, BF3Server.free_slots.values(), 'FREE SLOTS')

        # Preset List
        preset_check_box, preset_widget = self.make_layout(3, BF3Server.preset.values(), 'PRESET')

        browse_button = QtGui.QPushButton('Browse')
        default_button = QtGui.QPushButton('Default')
        button_hbox = QtGui.QHBoxLayout()
        button_hbox.addWidget(default_button)
        button_hbox.addStretch(1)
        button_hbox.addWidget(browse_button)

        hbox = QtGui.QHBoxLayout()

        vbox_inner = QtGui.QVBoxLayout()
        vbox_inner.addWidget(mode_widget)
        vbox_inner.addWidget(game_size_widget)
        vbox_inner.addWidget(free_slots_widget)
        vbox_inner.addWidget(preset_widget)

        hbox.addLayout(vbox_inner)
        hbox.addWidget(map_widget)

        vbox.addLayout(hbox)
        vbox.addStretch(0)
        vbox.addLayout(button_hbox)

        self.setLayout(vbox)

    def make_layout(self, col, label_list, group_box_label):
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




app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
window.setFixedSize(window.size())
app.exec_()