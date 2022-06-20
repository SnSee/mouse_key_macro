from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout
from utils.key_transfer import qt_trans_key
from decorations.buttons import get_button


# 记录按键对话框
# noinspection PyArgumentList
class KeyRecorder(QDialog):
    key_chose = pyqtSignal(str)

    def __init__(self):
        super(KeyRecorder, self).__init__()
        self.setModal(True)
        lay = QVBoxLayout()
        lay.addWidget(QLabel("按下快捷键", self))
        lay.addSpacing(20)
        lay.addWidget(get_button(self, self._clear, "清空"))
        self.setLayout(lay)

    def _clear(self):
        # noinspection all
        self.key_chose.emit("")
        self.close()

    def keyPressEvent(self, e) -> None:
        key = e.key()
        key = chr(key).lower() if key < 256 else qt_trans_key(key)
        if not key:
            QMessageBox.warning(self, "Warning", "不支持按键")
            return
        # noinspection all
        self.key_chose.emit(key)
        self.close()
