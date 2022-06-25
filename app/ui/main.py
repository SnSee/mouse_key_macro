import sys
import logging
import threading
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from macro_manager import MacroMgr
from widgets.macro_widget import MacroWidget
from widgets.macro_batch_widget import MacroBatchWidget
from widgets.dock_widget import DockWidget


# noinspection PyArgumentList
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._listening = False          # 反映监听状态，False时快捷键无法触发录制
        self._cur_macro_thread = None    # 宏线程，同一间只有一个宏线程
        self._init_ui()
        self.setFixedSize(460, 460)

    def _init_ui(self):
        self._init_menu()
        self._init_dock()

        self._listen_btn = QPushButton(self)
        self._update_listen_btn()
        # noinspection all
        self._listen_btn.clicked.connect(self._switch_listening_status)

        # noinspection all
        self._macro_widget = MacroWidget(self)
        self._macro_widget.propose_end.connect(self._listen)
        # noinspection all
        self._batch_widget = MacroBatchWidget(self)
        self._setting_dialog = None

        self._tabs = QTabWidget(self)
        self._tabs.addTab(self._macro_widget, "宏")
        self._tabs.addTab(self._batch_widget, "宏组")

        lay_switch = QHBoxLayout()
        lay_switch.addWidget(self._listen_btn)

        lay = QVBoxLayout()
        lay.addLayout(lay_switch)
        lay.addWidget(self._tabs)
        cw = QWidget()
        cw.setLayout(lay)
        self.setCentralWidget(cw)

    def _init_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction("设置", self._open_setting)

        win_menu = self.menuBar().addMenu("窗口")
        win_menu.addAction("打开日志", self._open_log)

    def _init_dock(self):
        self._dock_widget = DockWidget(self)
        self._dock_widget.setFixedHeight(180)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._dock_widget)
        if not MacroMgr.config().show_log:
            self._dock_widget.hide()

    def _switch_listening_status(self):
        self._listening = not self._listening
        self._listen() if self._listening else self._stop_listen()
        self._update_listen_btn()
        self._tabs.setEnabled(not self._listening)

    # 宏录制线程
    def _listen(self):
        self._cur_macro_thread = threading.Thread(target=MacroMgr.keep_imitate_listen)
        self._cur_macro_thread.start()

    def _stop_listen(self):
        MacroMgr.stop_listen()
        self._cur_macro_thread.join()

    def _update_listen_btn(self):
        self._listen_btn.setText("关闭监听" if self._listening else "开启监听")

    def _open_setting(self):
        if not self._setting_dialog:
            from dialogs.setting_dialog import SettingDialog
            self._setting_dialog = SettingDialog(self)
        self._setting_dialog.exec()

    def _open_log(self):
        self._dock_widget.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self._listening:
            self._switch_listening_status()
        MacroMgr.config().show_log = self._dock_widget.isVisible()
        MacroMgr.save_to_file()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    app = QApplication(sys.argv)
    # noinspection all
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setFont(QtGui.QFont("微软雅黑", 10))
    win = MainWindow()
    win.show()
    app.exec()
