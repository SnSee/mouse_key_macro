import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu
from macro_manager import MacroMgr
from utils.logging_qt import QLogHandler
from utils.translator import string_to_level, level_to_string


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
        lay = QVBoxLayout()
        lay.addWidget(self._text_edit)
        self.setLayout(lay)
        self._init_context_menu()

    def _init_context_menu(self):
        clear_act = QAction("清空日志", self)
        clear_act.triggered.connect(self._text_edit.clear)
        level_group = QActionGroup(self)
        level_menu = QMenu(self)
        level_menu.addAction(level_group.addAction(level_to_string(logging.DEBUG)))
        level_menu.addAction(level_group.addAction(level_to_string(logging.INFO)))
        level_menu.addAction(level_group.addAction(level_to_string(logging.WARNING)))
        level_menu.addAction(level_group.addAction(level_to_string(logging.ERROR)))
        for a in level_group.actions():
            a.setCheckable(True)
        level_group.triggered.connect(self._set_level)
        for action in level_group.actions():
            if string_to_level(action.text()) == MacroMgr.config().log_level:
                self._set_level(action)
                break
        log_level_act = QAction("日志等级", self)
        log_level_act.setMenu(level_menu)
        # 自定义右键菜单
        self._text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self._text_edit.addAction(clear_act)
        self._text_edit.addAction(log_level_act)

    @staticmethod
    def _set_level(action: QAction):
        action.setChecked(True)
        MacroMgr.config().log_level = string_to_level(action.text())
