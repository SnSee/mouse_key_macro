from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QCheckBox
from PyQt5.QtWidgets import QVBoxLayout

from macro_manager import MacroMgr


class SettingDialog(QDialog):
    def __init__(self, parent):
        super(SettingDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("设置")
        self._init_ui()

    def _init_ui(self):
        sound_trigger = QCheckBox("开启声音", self)
        enable_sound = Qt.Checked if MacroMgr.get_sound_enabled() else Qt.Unchecked
        sound_trigger.setCheckState(enable_sound)
        sound_trigger.stateChanged.connect(self._on_sound_checked)

        lay = QVBoxLayout()
        lay.addWidget(sound_trigger)
        self.setLayout(lay)

    @staticmethod
    def _on_sound_checked(check_state: Qt.CheckState):
        MacroMgr.set_sound_enabled(check_state == Qt.Checked)
