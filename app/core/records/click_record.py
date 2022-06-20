import logging
from pynput import mouse, keyboard
from globals.config import GlobalConfig
from utils.key_transfer import *
from utils.time_helper import waste_time

mouse_ctrl = mouse.Controller()     # 鼠标控制器
key_ctrl = keyboard.Controller()    # 键盘控制器


class ClickRecord:

    def __init__(self, delay: float, pressed: bool, key_or_button):
        self._delay = delay                     # 距离上次press/release多久
        self._pressed = pressed                 # 是press还是release
        self._key_or_button = key_or_button     # 对应按键

    def __str__(self):
        text = pynput_key_to_string(self._key_or_button)
        return f"{self._delay},{self._pressed},{text}"

    @property
    def delay(self):
        return self._delay

    @staticmethod
    def _press(self):
        raise NotImplementedError()

    @staticmethod
    def _release(self):
        raise NotImplementedError()

    def on_retain(self):
        raise NotImplementedError()

    def imitate(self):
        waste_time(self._delay)
        operation = self._press if self._pressed else self._release
        operation(self._key_or_button)


class MouseClickRecord(ClickRecord):
    def __init__(self, delay: float, pressed: bool, button: mouse.Button):
        super(MouseClickRecord, self).__init__(delay, pressed, button)

    @staticmethod
    def _press(button):
        if not GlobalConfig.dd_mode:
            logging.debug(f"press button: {str(button)}")
            mouse_ctrl.press(button)
            return
        from dd.dd_manager import DDManager
        DDManager.press_mouse(button)

    @staticmethod
    def _release(button):
        if not GlobalConfig.dd_mode:
            logging.debug(f"release button: {str(button)}")
            mouse_ctrl.release(button)
            return
        from dd.dd_manager import DDManager
        DDManager.release_mouse(button)

    def on_retain(self):
        pass


class KeyboardClickRecord(ClickRecord):
    def __init__(self, delay: float, pressed: bool, key: keyboard.Key or str):
        super(KeyboardClickRecord, self).__init__(delay, pressed, key)

    @staticmethod
    def _press(key):
        if not GlobalConfig.dd_mode:
            key_ctrl.press(key)
            return
        from dd.dd_manager import DDManager
        DDManager.press_key(pynput_key_to_string(key))

    @staticmethod
    def _release(key):
        if not GlobalConfig.dd_mode:
            key_ctrl.release(key)
            return
        from dd.dd_manager import DDManager
        DDManager.release_key(pynput_key_to_string(key))

    def on_retain(self):
        pass
