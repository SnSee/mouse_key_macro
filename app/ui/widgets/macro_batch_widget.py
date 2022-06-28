from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox
from globals.name import Name
from macro_manager import MacroMgr
from decorations.macro_batch_table import MacroBatchTable


class MacroBatchWidget(QWidget):
    def __init__(self, parent):
        super(MacroBatchWidget, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self._add_btn = QPushButton("新建宏组", self)
        self._add_btn.clicked.connect(self._create_batch)
        del_btn = QPushButton("全部删除", self)
        del_btn.clicked.connect(self._on_del_all_macros)
        self._batch_table = MacroBatchTable(self)
        lay_btn = QHBoxLayout()
        lay_btn.addWidget(self._add_btn)
        lay_btn.addWidget(del_btn)
        lay = QVBoxLayout()
        lay.addLayout(lay_btn)
        lay.addWidget(self._batch_table)
        self.setLayout(lay)
        self._init_batch_table()

    def _init_batch_table(self):
        self._batch_table.reset_content()

    def _create_batch(self):
        self._batch_table.add_batch(Name.default_name(), "")

    # 删除所有宏组
    def _on_del_all_macros(self):
        # 弹出确认对话框
        answer = QMessageBox.question(self, "删除宏", f"是否确认删除所有宏组")
        if answer == QMessageBox.Yes:
            MacroMgr.del_all_batches()
            self._init_batch_table()
