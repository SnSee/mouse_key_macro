import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QMessageBox, QComboBox
from macro_manager import MacroMgr
from decorations.buttons import get_ok_button, get_trash_button


class ChooseMacroDialog(QDialog):
    def __init__(self, parent):
        super(ChooseMacroDialog, self).__init__(parent)
        self._batch_name = None
        self._table_connected = False   # _table信号是否绑定槽
        self._macro_names = []          # 所有可用宏名
        self._init_ui()
        self.setMinimumWidth(400)

    @property
    def batch_name(self):
        return self._batch_name

    @batch_name.setter
    def batch_name(self, name):
        self._batch_name = name

    def _init_ui(self):
        add_btn = QPushButton("添加宏")
        add_btn.clicked.connect(self._on_add_macro)
        labels = ("宏名", "重复次数", "相对模式", "删除")
        self._table = QTableWidget(self)
        self._table.setColumnCount(len(labels))
        self._table.setHorizontalHeaderLabels(labels)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(2, 80)
        lay = QVBoxLayout()
        lay.addWidget(add_btn)
        lay.addWidget(self._table)
        lay.addWidget(get_ok_button(self, self._on_ok))
        self.setLayout(lay)
        self._connect_table()

    def _connect_table(self):
        if self._table_connected:
            return
        self._table.itemChanged.connect(self._on_item_changed)
        self._table_connected = True

    def _disconnect_table(self):
        if not self._table_connected:
            return
        self._table.itemChanged.disconnect()
        self._table_connected = False

    def _on_ok(self):
        macros = []
        for i in range(self._table.rowCount()):
            macro_name = self._table.cellWidget(i, 0).currentText().strip()
            if not MacroMgr.has_macro_name(macro_name):
                logging.warning(f"宏名 {macro_name} 不存在")
                return
            times = self._table.item(i, 1).text()
            if not times.isnumeric():
                logging.warning(f"重复次数 {times} 不是数字")
                return
            if not MacroMgr.has_macro_name(macro_name):
                QMessageBox.warning(self, "警告", f"不存在宏 {macro_name}")
                return
            state = self._table.cellWidget(i, 2).checkState()
            macros.append([macro_name, int(times), state == Qt.Checked])
        MacroMgr.clear_batch_macros(self._batch_name)
        for macro_name, times, relative in macros:
            MacroMgr.add_macro_to_batch(self._batch_name, macro_name, times, relative)
        self.close()

    def _on_add_macro(self):
        self._add_row("", 1, False)

    def _on_item_changed(self, item: QTableWidgetItem):
        col = item.column()
        text = item.text().strip()
        if col == 0:    # 检查宏名是否合法
            if not MacroMgr.has_macro_name(text):
                QMessageBox.warning(self, "警告", f"不存在宏 {text}")
        elif col == 1:
            if not text.isnumeric():
                QMessageBox.warning(self, "警告", f"次数必须为整数")

    def _add_row(self, macro_name: str, times: int, relative_mod: bool):
        self._disconnect_table()
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem())
        self._table.setItem(row, 1, QTableWidgetItem(str(times)))
        self._table.setItem(row, 2, QTableWidgetItem(""))
        self._table.setItem(row, 3, QTableWidgetItem(""))
        cb = QCheckBox(self)
        cb.setCheckState(Qt.Checked if relative_mod else Qt.Unchecked)
        choose_combox = QComboBox(self)
        choose_combox.setEditable(True)
        choose_combox.addItems(MacroMgr.macro_names)
        choose_combox.setCurrentText(macro_name)
        self._table.setCellWidget(row, 0, choose_combox)
        self._table.setCellWidget(row, 2, cb)
        self._table.setCellWidget(row, 3, get_trash_button(self, self._del_cur_line, True))
        self._connect_table()

    def _del_cur_line(self):
        row = self._table.currentRow()
        self._table.removeRow(row)

    def showEvent(self, e) -> None:
        self._table.setRowCount(0)
        self._table.clearContents()
        # 加载宏组中的宏
        batch = MacroMgr.get_batch(self._batch_name)
        if batch:
            for macro, times, relative in batch.macros:
                self._add_row(macro.name, times, relative)
        return super(ChooseMacroDialog, self).showEvent(e)
