from PySide import QtCore
from PySide import QtGui
from bf3 import BF3Server

import sys


class MainWindow(QtGui.QDialog):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('BF3 Server Pinger')
        # Main Vertical Box Layout
        vbox = QtGui.QVBoxLayout()

        # Maps List
        map_check_box, map_group_box = self.make_layout(col=2, label_list=BF3Server.map_code.values(),
                                                        group_box_label='MAPS')

        # Mode List
        mode_check_box, mode_group_box = self.make_layout(col=2, label_list=BF3Server.game_mode.values(),
                                                          group_box_label='MODE')

        # Game Size List


        temp_grid = QtGui.QGridLayout()
        temp_grid.addWidget(mode_group_box, 0, 0)
        temp_grid.addWidget(map_group_box, 0, 1, 2)

        self.setLayout(temp_grid)

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