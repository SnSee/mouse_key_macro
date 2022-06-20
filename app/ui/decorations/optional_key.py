from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLineEdit
from dialogs.key_recorder_dialog import KeyRecorder


# 点击后可选择快捷键
class OptionalKey(QLineEdit):
    key_set = pyqtSignal()

    def __init__(self, parent, switch_key=""):
        super().__init__(parent)
        self.setReadOnly(True)
        # 禁用右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.current_key = switch_key  # 当前按键
        self.setPlaceholderText("选择快捷键")
        self.setFixedHeight(25)
        self.setText(self.current_key)

    def _on_key_chose(self, key: str):
        self.current_key = key
        self.setText(self.current_key)
        # noinspection all
        self.key_set.emit()

    def mousePressEvent(self, e) -> None:
        if e.button() != Qt.LeftButton:
            return
        kr = KeyRecorder()
        # noinspection all
        kr.key_chose.connect(self._on_key_chose)
        kr.exec()

    def clear(self):
        self.current_key = ""
        self.setText(self.current_key)
