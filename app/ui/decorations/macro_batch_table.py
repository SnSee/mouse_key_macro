from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox

from macro_manager import MacroMgr
from dialogs.choose_macro_dialog import ChooseMacroDialog
from dialogs.key_recorder_dialog import KeyRecorder
from decorations.buttons import get_trash_button


class MacroBatchTable(QTableWidget):
    def __init__(self, parent):
        super(MacroBatchTable, self).__init__(parent)
        self._init_ui()
        self._key_recorder = KeyRecorder()
        self._key_recorder.key_chose.connect(self._hot_key_chose)
        self._default_trigger = self.editTriggers()

    def _init_ui(self):
        self._choose_macro_dlg = None
        header_labels = ("名称", "触发按键", "编辑", "删除", "备注")
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 40)
        self.setColumnWidth(3, 40)
        # 单元格不可选中
        self.setSelectionMode(QTableWidget.NoSelection)
        self.itemClicked.connect(self._item_clicked)
        self.itemChanged.connect(self._item_changed)

    def _set_text(self, item: QTableWidgetItem, text: str):
        self.itemChanged.disconnect(self._item_changed)
        item.setText(text)
        self.itemChanged.connect(self._item_changed)

    def _edit_macros(self):
        if not self._choose_macro_dlg:
            self._choose_macro_dlg = ChooseMacroDialog(self)
        self._choose_macro_dlg.batch_name = self.item(self.currentRow(), 0).text().strip()
        self._choose_macro_dlg.exec()

    def _delete_check(self, row: int):
        batch_name = self.item(row, 0).text()
        answer = QMessageBox.question(self, "删除宏组", f"是否确认删除宏组 {batch_name}")
        if answer == QMessageBox.Yes:
            batch_name = self.item(row, 0).text()
            self.removeRow(row)
            MacroMgr.del_batch(batch_name)

    def _hot_key_chose(self, key: str):
        batch_name = self.item(self.currentRow(), 0).text()
        if MacroMgr.set_batch_hot_key(batch_name, key):
            self._set_text(self.currentItem(), key)

    def _item_clicked(self, item: QTableWidgetItem):
        if item.column() == 1:
            self._key_recorder.show()
        elif item.column() == 2:
            self._edit_macros()
        elif item.column() == 3:
            self._delete_check(item.row())

    def _item_changed(self, item: QTableWidgetItem):
        row, col = item.row(), item.column()
        batch_name = self.item(row, 0).text().strip()
        if col == 0:
            if not MacroMgr.rename_batch(row, batch_name):
                self._set_text(item, MacroMgr.get_batch_name(row))
        elif col == self.columnCount() - 1:
            MacroMgr.set_batch_desc(batch_name, self.item(row, self.columnCount() - 1).text().strip())

    def _add_batch(self, name, hot_key, desc):
        self.itemChanged.disconnect(self._item_changed)
        row_count = self.rowCount()
        self.insertRow(row_count)
        self.setItem(row_count, 0, QTableWidgetItem(name))
        self.setItem(row_count, 1, QTableWidgetItem(hot_key))
        self.setItem(row_count, 2, QTableWidgetItem("编辑"))
        self.setItem(row_count, 3, QTableWidgetItem(""))
        self.setItem(row_count, 4, QTableWidgetItem(desc))
        trash_btn = get_trash_button(self, None, True)
        trash_btn.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setCellWidget(row_count, 3, trash_btn)
        self.itemChanged.connect(self._item_changed)

    def add_batch(self, name, hot_key, desc=""):
        MacroMgr.add_batch(name)
        if hot_key:
            MacroMgr.set_batch_hot_key(name, hot_key)
        self._add_batch(name, hot_key, desc)
        self.editItem(self.item(self.rowCount() - 1, 0))

    def reset_content(self):
        self.clearContents()
        self.setRowCount(0)
        for mb_name in MacroMgr.batch_names:
            mb = MacroMgr.get_batch(mb_name)
            self._add_batch(mb_name, mb.hot_key, mb.desc)
