from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMessageBox
from globals.name import Name
from macro_manager import MacroMgr
from decorations.macro_batch_table import MacroBatchTable


class MacroBatchWidget(QWidget):
    def __init__(self, parent):
        super(MacroBatchWidget, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self._add_btn = QPushButton("新建宏组", self)
        self._batch_table = MacroBatchTable(self)
        self._add_btn.clicked.connect(self._create_batch)
        lay = QVBoxLayout()
        lay.addWidget(self._add_btn)
        lay.addWidget(self._batch_table)
        self.setLayout(lay)

    def _init_batch_table(self):
        assert False

    def _create_batch(self):
        self._batch_table.add_batch(Name.default_name(), "")

    # 删除所有宏组
    def on_del_all_macros(self):
        # 弹出确认对话框
        answer = QMessageBox.question(self, "删除宏", f"是否确认删除所有宏")
        if answer == QMessageBox.Yes:
            MacroMgr.del_all_macros()
            self._init_batch_table()
