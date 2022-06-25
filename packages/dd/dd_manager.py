import os
import time
import logging
from ctypes import windll
from utils.key_transfer import dd_key_number


class DDManagerP:

    def __init__(self, dll_path):
        self.dd = None
        self._load_dll(dll_path)

    def _load_dll(self, dll_path):
        if not windll.shell32.IsUserAnAdmin():
            raise Exception("No administrator privileges")
        self.dd = windll.LoadLibrary(dll_path)
        if self.dd.DD_btn(0) != 1:
            raise Exception("Failed to load dd driver.")

    def press_mouse(self, button: str):
        if not isinstance(button, str):
            button = str(button)
        logging.debug(f"press button: {button}")
        if "left" in button:
            self.dd.DD_btn(1)   # 按下左键
        elif "right" in button:
            self.dd.DD_btn(4)   # 按下右键

    def release_mouse(self, button: str):
        if not isinstance(button, str):
            button = str(button)
        if "left" in button:
            self.dd.DD_btn(2)   # 松开左键
        elif "right" in button:
            self.dd.DD_btn(8)   # 松开右键

    def click(self):
        self.dd.DD_key(1)   # 按下左键
        self.dd.DD_key(2)   # 松开左键

    def right_click(self):
        self.dd.DD_btn(4)   # 按下左键
        self.dd.DD_btn(8)   # 松开左键

    def press_key(self, key: str):
        if not isinstance(key, str):
            key = str(key)  # 使用pynput.keyboard.Key中定义的按键类型
        key_num = dd_key_number(key)
        self.dd.DD_key(key_num, 1)

    def release_key(self, key: str):
        if not isinstance(key, str):
            key = str(key)  # 使用pynput.keyboard.Key中定义的按键类型
        key_num = dd_key_number(key)
        self.dd.DD_key(key_num, 2)

    # duration: 按下时间，单位ms
    def click_key(self, key: str, duration=0):
        if not isinstance(key, str):
            key = str(key)  # 使用pynput.keyboard.Key中定义的按键类型
        key_num = dd_key_number(key)
        self.dd.DD_key(key_num, 1)
        if duration:
            time.sleep(duration / 1000)
        self.dd.DD_key(key_num, 2)

    def mov(self, point):
        x = point.x if hasattr(point, "x") else point[0]
        y = point.x if hasattr(point, "y") else point[1]
        self.dd.DD_mov(x, y)

    def mov_r(self, point):
        x = point.x if hasattr(point, "x") else point[0]
        y = point.x if hasattr(point, "y") else point[1]
        self.dd.DD_movR(x, y)


DDManager = DDManagerP(os.path.join(os.path.dirname(__file__), "DD94687.64.dll"))
