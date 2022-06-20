import logging
from pynput import mouse
from globals.config import GlobalConfig
from utils.time_helper import waste_time


mouse_ctrl = mouse.Controller()     # 鼠标控制器


class MoveRecord:

    def __init__(self, delay: float, x: int, y: int):
        self.x = x
        self.y = y
        self.delay = delay  # 距离上次move多久

    def __str__(self):
        return f"{self.delay},{self.x},{self.y}"

    def on_retain(self):
        pass

    # last_record: 上一个记录点，如果非None说明以相对模式移动
    def imitate(self, last_move_record=None):
        waste_time(self.delay)
        if last_move_record:
            x = self.x - last_move_record.x
            y = self.y - last_move_record.y
        else:
            x = self.x - mouse_ctrl.position[0]
            y = self.y - mouse_ctrl.position[1]
        # 此时x, y都是相对值
        logging.debug(f"target move: {self.x}, {self.y}")
        logging.debug(f"relative move: {x}, {y}")
        if not GlobalConfig.dd_mode:
            mouse_ctrl.move(x, y)  # pynput只有相对移动接口
            return
        from dd.dd_manager import DDManager
        # dd使用绝对移动(使用相对移动有问题)
        DDManager.mov((x + mouse_ctrl.position[0], y + mouse_ctrl.position[1]))
