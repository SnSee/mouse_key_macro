from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from macro_manager import MacroMgr
from dialogs.key_recorder_dialog import KeyRecorder
from decorations.buttons import get_trash_button


# 宏展示界面
# noinspection PyArgumentList
class MacroTable(QTableWidget):
    def __init__(self, parent):
        super(MacroTable, self).__init__(parent)
        self._key_recorder = KeyRecorder()
        self._key_recorder.key_chose.connect(self._on_hot_key_chose)
        self.setAutoScroll(True)
        self.setRowCount(0)
        header_labels = ("名称", "触发按键", "相对模式", "删除", "备注")
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        # noinspection all
        self.itemClicked.connect(self._on_item_clicked)
        self.itemChanged.connect(self._on_item_changed)

    def _on_item_clicked(self, item: QTableWidgetItem):
        name = self.itemAt(item.row(), 0).text()
        if item.column() == 1:
            self._key_recorder.show()
        elif item.column() == 2:
            MacroMgr.set_macro_relative(name, True if item.checkState() == Qt.Checked else False)

    def _on_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            if not MacroMgr.rename_macro(item.row(), item.text().strip()):
                item.setText(MacroMgr.get_macro_name(item.row()))
        elif item.column() == self.columnCount() - 1:
            macro_name = self.item(item.row(), 0).text().strip()
            MacroMgr.set_macro_desc(macro_name, item.text().strip())

    def _on_hot_key_chose(self, key: str):
        macro_name = self.item(self.currentRow(), 0).text().strip()
        if MacroMgr.set_hot_key(macro_name, key):
            self.currentItem().setText(key)

    def _delete_check(self):
        row = self.currentRow()
        name = self.itemAt(row, 0).text()
        answer = QMessageBox.question(self, "删除宏", f"是否确认删除宏 {name}")
        if answer == QMessageBox.Yes:
            if MacroMgr.del_macro(name):
                self.removeRow(row)

    def add_macro(self, name: str, hot_key: str, desc=""):
        self.itemClicked.disconnect(self._on_item_clicked)
        self.itemChanged.disconnect(self._on_item_changed)
        row_count = self.rowCount()
        self.insertRow(row_count)
        relative_item = QTableWidgetItem()
        relative_item.setCheckState(Qt.Unchecked)
        self.setItem(row_count, 0, QTableWidgetItem(name))
        self.setItem(row_count, 1, QTableWidgetItem(hot_key))
        self.setItem(row_count, 2, relative_item)
        self.setItem(row_count, 3, QTableWidgetItem())
        self.setItem(row_count, 4, QTableWidgetItem(desc))
        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 60)
        self.setColumnWidth(3, 60)
        self.setCellWidget(row_count, 3, get_trash_button(self, self._delete_check, True))
        self.itemClicked.connect(self._on_item_clicked)
        self.itemChanged.connect(self._on_item_changed)
