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
        self._dd_switch = QCheckBox("使用dd按键", self)
        self._dd_switch.setCheckState(Qt.Checked if MacroMgr.config().dd_mode else Qt.Unchecked)
        self._dd_switch.stateChanged.connect(self._set_dd_mode)
        self._listen_btn = QPushButton(self)
        self._update_listen_btn()
        self._listen_btn.clicked.connect(self._switch_listening_status)

        self._macro_widget = MacroWidget(self)
        self._macro_widget.propose_end.connect(self._listen)
        self._batch_widget = MacroBatchWidget(self)
        self._dock_widget = DockWidget(self)
        self._dock_widget.setFixedHeight(180)
        self._setting_dialog = None

        self._init_menu()

        self._tabs = QTabWidget(self)
        self._tabs.addTab(self._macro_widget, "宏")
        self._tabs.addTab(self._batch_widget, "宏组")

        lay_switch = QHBoxLayout()
        lay_switch.addWidget(self._dd_switch)
        lay_switch.addWidget(self._listen_btn)

        lay = QVBoxLayout()
        lay.addLayout(lay_switch)
        lay.addWidget(self._tabs)
        cw = QWidget()
        cw.setLayout(lay)
        self.setCentralWidget(cw)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._dock_widget)

    def _init_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction("设置", self._open_setting)

    def _set_dd_mode(self, use_dd):
        if not use_dd:
            MacroMgr.config().dd_mode = False
            return
        # 检查是否具有管理员权限
        from ctypes import windll
        if not windll.shell32.IsUserAnAdmin():
            QMessageBox.warning(self, "Warning", "以管理员身份运行才能使用dd按键")
            self._dd_switch.setCheckState(Qt.Unchecked)
            return
        MacroMgr.config().dd_mode = True

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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        MacroMgr.save_to_file()
        if self._listening:
            self._switch_listening_status()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setFont(QtGui.QFont("微软雅黑", 10))
    win = MainWindow()
    win.show()
    app.exec()
