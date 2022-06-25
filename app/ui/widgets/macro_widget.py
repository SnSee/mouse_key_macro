import threading
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from macro_manager import MacroMgr
from dialogs.propose_macro_dialog import CreateDialog
from decorations.optional_key import OptionalKey
from decorations.macro_table import MacroTable


# 宏操作主界面
# noinspection PyArgumentList
class MacroWidget(QWidget):
    macro_end = pyqtSignal()
    propose_end = pyqtSignal()

    def __init__(self, parent):
        super(MacroWidget, self).__init__(parent)
        self._lock = threading.Lock()    # 宏录制线程锁
        self._propose_dlg = None         # 录制结束处理宏窗口
        self._init_ui()
        MacroMgr.set_callback(self._on_macro_end)

    def _init_ui(self):
        self._macro_table = MacroTable(self)  # 宏表格
        self._optional_key = OptionalKey(self, MacroMgr.switch_key)  # 快捷键选择窗口
        # noinspection all
        self._optional_key.key_set.connect(self._on_switch_key_set)

        lay_switch = QHBoxLayout()
        lay_switch.addSpacing(50)
        lay_switch.addWidget(QLabel("录制快捷键："))
        lay_switch.addWidget(self._optional_key)
        lay_switch.addSpacing(50)
        lay = QVBoxLayout()
        lay.addLayout(lay_switch)
        lay.addWidget(self._macro_table)
        self.setLayout(lay)

        # noinspection all
        self.macro_end.connect(self._propose_macro)
        self._init_macros()

    def _init_macros(self):
        for macro in MacroMgr.all_macros.values():
            self._macro_table.add_macro(macro.name, macro.hot_key, macro.desc)

    def _on_switch_key_set(self):
        MacroMgr.switch_key = self._optional_key.current_key

    # 宏录制完回调
    def _on_macro_end(self):
        # noinspection all
        self.macro_end.emit()

    def _propose_macro(self):
        self._lock.acquire()
        if not self._propose_dlg:
            self._propose_dlg = CreateDialog(self)
            # noinspection all
            self._propose_dlg.name_set.connect(self._retain_macro)
        self._propose_dlg.exec()
        self._lock.release()
        # noinspection all
        self.propose_end.emit()

    # 保留当前录制的宏
    def _retain_macro(self, name: str, hot_key: str):
        MacroMgr.retain_current(name, hot_key)
        self._macro_table.add_macro(name, hot_key)
