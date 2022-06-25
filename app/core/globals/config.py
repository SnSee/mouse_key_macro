import logging
import pyautogui


class _GlobalConfig:
    MACRO_DIR = "../../.macros"
    MACRO_CONFIG = "macro.json"

    def __init__(self):
        self._dd_mode = False           # 是否使用dd驱动模拟键鼠
        self._screen_size = pyautogui.size()

    @property
    def dd_mode(self):
        return self._dd_mode

    @dd_mode.setter
    def dd_mode(self, use_dd):
        self._dd_mode = use_dd
        if use_dd:
            from ctypes import windll
            if not windll.shell32.IsUserAnAdmin():
                logging.warning("如果要使用dd模拟需要以管理员身份运行")
                self._dd_mode = False

    @property
    def screen_size(self):
        return self._screen_size

    def to_dict(self):
        return {"dd_mode": self.dd_mode}

    def from_dict(self, data: dict):
        if data.get("dd_mode", False):
            from ctypes import windll
            if windll.shell32.IsUserAnAdmin():
                self.dd_mode = True


GlobalConfig = _GlobalConfig()
