import os
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QProgressBar
from config_data import current_config
from abspath import abspath
from helper.helper import get_right_map


class ProgressBar(QProgressBar):
    def __init__(self, parent):
        super(ProgressBar, self).__init__(parent)
        self.main_window = parent
        self.default_x = 0
        self.default_y = 420
        self.default_width = 830
        self.default_height = 40
        self.default_fontsize = 250
        self.notification = {"done": QSound(os.path.join(abspath, "res/success.wav")),
                             "error": QSound(os.path.join(abspath, "res/fail.wav")),
                             ".": QSound("blank")}

        self.setGeometry(self.default_x, self.default_y, self.default_width, self.default_height)

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.text = QLabel(self)
        self.text.setStyleSheet(
            "QLabel{font-size: %ipt; font-weight: bold; color: white; background-color: transparent;}QToolTip { background-color:white;color: black; }" % self.default_fontsize)

        self.setStyleSheet("""
QProgressBar {
	border: 2px solid white;
	border-radius: 5px;
	color:white;	
}

QProgressBar::chunk {
	background-color: rgba(226, 107, 167, 255);
}""")

    def directory_changed(self, path):
        print('Directory Changed:', path)

    def file_changed(self, path):

        f = open(path, "r")
        content = f.read()
        if content in self.notification:
            self.notification[content].play()
            self.hide()
            self.setValue(0)
            if self.main_window.mode == "queue_mode" and os.stat('queue_list.txt').st_size == 0:
                self.main_window.mode = "no_queue"
                print("queue is empty")
                return
            if self.main_window.mode == "queue_mode":
                with open('queue_list.txt', 'r') as fin:
                    data = fin.read().splitlines(True)
                    filename = data[0].strip("\n")

                with open('queue_list.txt', 'w') as fout:
                    fout.writelines(data[1:])

                self.main_window.setreplay(filename)

                mappath = get_right_map(filename)
                if mappath is not None:
                    self.main_window.setmap(mappath)
                print("finished")
                if self.main_window.startbutton.proc is None or self.main_window.startbutton.proc.poll() is not None:
                    self.main_window.startbutton.mouseclicked()
                    return

        self.setValue(max(self.value(), float("0" + content)))
        print(self.value())
        f.close()

    # if self.value() >= 100:
    # 	self.hide()
    # 	self.setValue(0)

    def hide(self):
        self.main_window.startbutton.default_y = 370
        self.main_window.startbutton.show()
        self.main_window.cancelbutton.hide()
        self.main_window.options.default_y = 430
        self.main_window.updatebutton.default_y = 400
        self.main_window.resizeEvent(True)
        super().hide()

    def show(self):
        mapendtime = "Max" if current_config['End time'] == -1 else current_config['End time']
        self.text.setToolTip(f"Map start time: {current_config['Start time']}, Map end time: {mapendtime}")
        self.main_window.startbutton.default_y = 330
        self.main_window.options.default_y = 390
        self.main_window.updatebutton.default_y = 360
        self.main_window.resizeEvent(True)
        self.main_window.startbutton.hide()
        self.main_window.cancelbutton.show()
        super().show()

    def changesize(self):
        scale = self.main_window.height() / self.main_window.default_height
        width = self.default_width * scale
        height = self.default_height * scale
        x = self.default_x * scale
        y = self.default_y * scale

        self.setGeometry(x, y, width, height)
        self.text.setGeometry(0, 0, width, height)
