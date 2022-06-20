from PyQt5.QtWidgets import QDialog


class SettingDialog(QDialog):
    def __init__(self, parent):
        super(SettingDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("设置")
