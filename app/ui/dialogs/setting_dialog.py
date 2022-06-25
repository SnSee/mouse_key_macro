from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from macro_manager import MacroMgr


class SettingDialog(QDialog):
    def __init__(self, parent):
        # noinspection all
        super(SettingDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("设置")
        self._init_ui()

    def _init_ui(self):
        self._dd_switch = QCheckBox("使用dd按键", self)
        self._dd_switch.setCheckState(Qt.Checked if MacroMgr.config().dd_mode else Qt.Unchecked)
        self._dd_switch.stateChanged.connect(self._set_dd_mode)

        sound_trigger = QCheckBox("开启声音", self)
        enable_sound = Qt.Checked if MacroMgr.get_sound_enabled() else Qt.Unchecked
        sound_trigger.setCheckState(enable_sound)
        sound_trigger.stateChanged.connect(self._on_sound_checked)

        lay = QVBoxLayout()
        # noinspection all
        lay.addWidget(self._dd_switch)
        # noinspection all
        lay.addWidget(sound_trigger)
        self.setLayout(lay)

    def _set_dd_mode(self, use_dd):
        if not use_dd:
            MacroMgr.config().dd_mode = False
            return
        # 检查是否具有管理员权限
        from ctypes import windll
        if not windll.shell32.IsUserAnAdmin():
            # noinspection all
            QMessageBox.warning(self, "Warning", "以管理员身份运行才能使用dd按键")
            self._dd_switch.setCheckState(Qt.Unchecked)
            return
        MacroMgr.config().dd_mode = True

    @staticmethod
    def _on_sound_checked(check_state: Qt.CheckState):
        MacroMgr.set_sound_enabled(check_state == Qt.Checked)
