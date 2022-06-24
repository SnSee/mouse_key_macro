import sys
import logging
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QApplication, QStyleFactory
from macro_manager import MacroMgr
from widgets.macro_widget import MacroWidget
from widgets.macro_batch_widget import MacroBatchWidget
from widgets.dock_widget import DockWidget


# noinspection PyArgumentList
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._init_ui()
        self.setFixedSize(460, 460)

    def _init_ui(self):
        self._macro_widget = MacroWidget(self)
        self._batch_widget = MacroBatchWidget(self)
        self._dock_widget = DockWidget(self)
        self._dock_widget.setFixedHeight(180)
        self._setting_dialog = None

        self._init_menu()

        tabs = QTabWidget(self)
        tabs.addTab(self._macro_widget, "宏")
        tabs.addTab(self._batch_widget, "宏组")
        tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._dock_widget)

    def _init_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction("设置", self._open_setting)

    def _on_tab_changed(self, index: int):
        if index == 1:  # 如果正在监听，设置成只读模式
            self._batch_widget.set_enabled(not self._macro_widget.listening)

    def _open_setting(self):
        if not self._setting_dialog:
            from dialogs.setting_dialog import SettingDialog
            self._setting_dialog = SettingDialog(self)
        self._setting_dialog.exec()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        MacroMgr.save_to_file()
        self._macro_widget.on_close()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    MacroMgr.set_sound_enabled(True)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setFont(QtGui.QFont("微软雅黑", 10))
    win = MainWindow()
    win.show()
    app.exec()
