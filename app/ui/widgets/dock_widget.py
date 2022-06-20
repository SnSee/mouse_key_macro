from PyQt5.QtWidgets import QDockWidget, QTabWidget
from widgets.log_widget import LogWidget


# noinspection PyArgumentList
class DockWidget(QDockWidget):
    def __init__(self, parent):
        super(DockWidget, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self._tabs = QTabWidget(self)
        self._tabs.setTabsClosable(False)
        self._tabs.setTabPosition(QTabWidget.North)
        self._tabs.addTab(LogWidget(self._tabs), "日志")
        self.setWidget(self._tabs)
