from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox
from macro_manager import MacroMgr
from decorations.optional_key import OptionalKey


# 宏录制结束后处理界面 及 创建宏组界面
# noinspection PyArgumentList
class CreateDialog(QDialog):
    name_set = pyqtSignal(str, str)

    def __init__(self, parent, for_batch=False):
        super(CreateDialog, self).__init__(parent)
        self._name = QLineEdit("")
        self._name.setPlaceholderText("输入名称")
        self._hot_key = OptionalKey(self)
        self._init_ui()
        self._name.setFocus()
        self._for_batch = for_batch

    def _init_ui(self):
        ok_btn = QPushButton("确认", self)
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn = QPushButton("取消", self)
        cancel_btn.clicked.connect(self.close)
        lay_btn = QHBoxLayout()
        lay_btn.addWidget(ok_btn)
        lay_btn.addWidget(cancel_btn)

        lay = QVBoxLayout()
        lay.addWidget(self._name)
        lay.addWidget(self._hot_key)
        lay.addLayout(lay_btn)
        self.setLayout(lay)

    def _on_ok(self):
        text = self._name.text().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "无效名称")
            return
        key = self._hot_key.text()
        if self._for_batch and not MacroMgr.valid_batch_name(text):
            return
        if not self._for_batch and not MacroMgr.valid_macro_name(text):
            return
        if key and not MacroMgr.valid_hot_key(key):
            return
        # noinspection all
        self.name_set.emit(text, self._hot_key.current_key)
        self.close()

    def showEvent(self, e) -> None:
        self._name.setText("")
        self._hot_key.clear()
        self._name.setFocus()
