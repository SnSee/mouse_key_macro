from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget, QApplication, QStyle
from PyQt5.QtGui import QIcon


def get_button(parent: QWidget, on_click, text="", icon: QIcon = None, plain_background=False):
    btn = QPushButton(text, parent)
    if plain_background:
        btn.setFlat(True)
    if icon:
        btn.setIcon(icon)
    if on_click:
        btn.clicked.connect(on_click)
    return btn


def get_trash_button(parent: QWidget, on_click, plain_background=False):
    icon = QApplication.style().standardIcon(QStyle.SP_TrashIcon)
    return get_button(parent, on_click, icon=icon, plain_background=plain_background)


def get_ok_button(parent: QWidget, on_ok) -> QPushButton:
    return get_button(parent, on_ok, "确认")


# 确认， 取消
def get_question_button_layout(parent: QWidget, on_ok, on_cancel) -> QHBoxLayout:
    ok_btn = get_ok_button(parent, on_ok)
    cancel_btn = get_button(parent, on_cancel, "取消")
    lay = QHBoxLayout()
    lay.addWidget(ok_btn)
    lay.addWidget(cancel_btn)
    return lay
