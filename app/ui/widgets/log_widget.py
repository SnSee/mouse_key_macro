import logging
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QStyle, QApplication
from utils.logging_qt import QLogHandler


class LogWidget(QWidget):
    def __init__(self, parent):
        super(LogWidget, self).__init__(parent)
        self._init_ui()
        # 绑定root logger
        self._log_handler = QLogHandler()
        self._log_handler.new_message.connect(self._text_edit.append)
        logging.getLogger().addHandler(self._log_handler)

    def _init_ui(self):
        self._text_edit = QTextEdit(self)
        self._text_edit.setReadOnly(True)
        clear_btn = QPushButton("清空日志")
        clear_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_TrashIcon))
        clear_btn.clicked.connect(self._text_edit.clear)

        lay = QVBoxLayout()
        lay.addWidget(self._text_edit)
        lay.addWidget(clear_btn)
        self.setLayout(lay)
