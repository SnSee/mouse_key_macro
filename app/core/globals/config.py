import logging
import pyautogui
from utils.translator import level_to_string, string_to_level


class _GlobalConfig:
    MACRO_DIR = "../../.macros"
    MACRO_CONFIG = "macro.json"

    def __init__(self):
        self._dd_mode = False               # 是否使用dd驱动模拟键鼠
        self._show_log = True               # 是否显示日志窗口
        self._log_level = logging.WARNING   # 日志等级
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
    def show_log(self):
        return self._show_log

    @show_log.setter
    def show_log(self, show):
        self._show_log = show

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        if not level:
            level = logging.WARNING
        logging.getLogger().setLevel(level)
        self._log_level = level

    @property
    def screen_size(self):
        return self._screen_size

    def to_dict(self):
        return {
            "dd_mode": self.dd_mode,
            "show_log": self.show_log,
            "log_level": level_to_string(self.log_level)
        }

    def from_dict(self, data: dict):
        if data.get("dd_mode", False):
            from ctypes import windll
            if windll.shell32.IsUserAnAdmin():
                self.dd_mode = True
        self.show_log = data.get("show_log", True)
        self.log_level = string_to_level(data.get("log_level", ""))


GlobalConfig = _GlobalConfig()
