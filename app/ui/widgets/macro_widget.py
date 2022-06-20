import threading
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QCheckBox, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from macro_manager import MacroMgr
from dialogs.propose_macro_dialog import CreateDialog
from decorations.optional_key import OptionalKey
from decorations.macro_table import MacroTable


# 宏操作主界面
# noinspection PyArgumentList
class MacroWidget(QWidget):
    macro_end = pyqtSignal()

    def __init__(self, parent):
        super(MacroWidget, self).__init__(parent)
        self._listening = False          # 反映监听状态，False时快捷键无法触发录制
        self._lock = threading.Lock()    # 宏录制线程锁
        self._cur_macro_thread = None    # 宏线程，同一间只有一个宏线程
        self._propose_dlg = None         # 录制结束处理宏窗口
        self._init_ui()
        MacroMgr.set_callback(self._on_macro_end)

    @property
    def listening(self):
        return self._listening

    def _init_ui(self):
        # hint_lab = QLabel("开启监听后敲击触发按键开始录制", self)
        self._dd_switch = QCheckBox("使用dd按键", self)
        self._dd_switch.stateChanged.connect(self._set_dd_mode)
        self._dd_switch.setCheckState(Qt.Checked if MacroMgr.config().dd_mode else Qt.Unchecked)
        self._macro_table = MacroTable(self)  # 宏表格
        self._optional_key = OptionalKey(self, MacroMgr.switch_key)  # 快捷键选择窗口
        # noinspection all
        self._optional_key.key_set.connect(self._on_switch_key_set)
        self.listen_btn = QPushButton(self)
        self.listen_btn.clicked.connect(self._switch_listening_status)

        lay_switch = QHBoxLayout()
        lay_switch.addWidget(self._dd_switch)
        lay_switch.addSpacing(50)
        lay_switch.addWidget(QLabel("录制快捷键："))
        lay_switch.addWidget(self._optional_key)
        lay_switch.addSpacing(50)
        lay_switch.addWidget(self.listen_btn)
        lay = QVBoxLayout()
        lay.addLayout(lay_switch)
        lay.addWidget(self._macro_table)
        self.setLayout(lay)

        self._update_listen_btn()
        # noinspection all
        self.macro_end.connect(self._propose_macro)
        self._init_macros()

    def _init_macros(self):
        for macro in MacroMgr.all_macros.values():
            self._macro_table.add_macro(macro.name, macro.hot_key, macro.desc)

    # 设置是否可交互
    def _set_enabled(self, enabled):
        self._dd_switch.setEnabled(enabled)
        self._optional_key.setEnabled(enabled)
        self._macro_table.setEnabled(enabled)

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

    def _update_listen_btn(self):
        self.listen_btn.setText("关闭监听" if self._listening else "开启监听")

    def _on_switch_key_set(self):
        MacroMgr.switch_key = self._optional_key.current_key

    # 宏录制完回调
    def _on_macro_end(self):
        # noinspection all
        self.macro_end.emit()

    # 宏录制线程
    def _listen(self):
        self._cur_macro_thread = threading.Thread(target=MacroMgr.keep_imitate_listen)
        self._cur_macro_thread.start()

    def _stop_listen(self):
        MacroMgr.stop_listen()
        self._cur_macro_thread.join()

    def _propose_macro(self):
        self._lock.acquire()
        if not self._propose_dlg:
            self._propose_dlg = CreateDialog(self)
            # noinspection all
            self._propose_dlg.name_set.connect(self._retain_macro)
        self._propose_dlg.exec()
        self._lock.release()
        self._listen()

    # 保留当前录制的宏
    def _retain_macro(self, name: str, hot_key: str):
        MacroMgr.retain_current(name, hot_key)
        self._macro_table.add_macro(name, hot_key)

    def _switch_listening_status(self):
        self._lock.acquire()
        self._listening = not self._listening
        self._listen() if self._listening else self._stop_listen()
        self._update_listen_btn()
        self._set_enabled(not self._listening)
        # 设置相关控件是否可互动
        self._lock.release()

    def on_close(self):
        if self._listening:
            self._switch_listening_status()
