import os
import time
import logging
from threading import Thread
from pynput import mouse, keyboard

from globals.config import GlobalConfig
from utils.key_transfer import *
from audio.audio_manager import AudioMgr
from records.move_record import MoveRecord
from records.click_record import MouseClickRecord, KeyboardClickRecord

mouse_ctrl = mouse.Controller()     # 鼠标控制器


class Macro:
    _extension = ".macro"

    def __init__(self, name=""):
        self._name = name
        self._hot_key = ""
        self._desc = ""
        self._file = ""                         # 对应磁盘文件
        self._enabled = True
        self._modified = False                  # 清空记录，新录制，重命名都算修改过
        self._records = []
        self._last_operation_time = None        # 上一次键鼠操作时间
        self._last_pos = None                   # 上一次鼠标位置
        self._relative_mode = False             # 复现轨迹时是否使用相对位置

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._modified = True
        self.remove_file()
        self._name = name

    @property
    def hot_key(self):
        return self._hot_key

    @hot_key.setter
    def hot_key(self, hot_key):
        self._modified = True
        self._hot_key = pynput_key_to_string(hot_key)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, desc):
        self._modified = True
        self._desc = desc

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, macro_file):
        self._modified = True
        self._file = macro_file

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enable):
        self._enabled = enable

    @property
    def relative_mode(self):
        return self._relative_mode

    @relative_mode.setter
    def relative_mode(self, relative_mode):
        logging.debug(f"Macro {self._name} relative: {relative_mode}")
        self._modified = True
        self._relative_mode = relative_mode

    def _delay(self):
        cur_time = time.time()
        delay = cur_time - self._last_operation_time
        self._last_operation_time = cur_time
        return delay

    def _add_record(self, record):
        self._records.append(record)

    def _save(self, file_path):
        # 如果宏没被修改过就不用重新保存
        if not self._modified:
            return
        assert file_path
        with open(file_path, "w") as fj:
            for rec in self._records:
                fj.write(str(rec))
                fj.write("\n")
        return

    def _load(self):
        if not os.path.exists(self._file):
            logging.error(f"不存在宏文件 {self._file}")
            return False
        with open(self._file) as fj:
            lines = fj.readlines()
        for line in lines:
            parts = line.strip().split(",")
            delay = float(parts[0])
            if parts[1].isnumeric():
                record = MoveRecord(delay, int(parts[1]), int(parts[2]))
            elif parts[2].startswith("Button"):
                record = MouseClickRecord(delay, parts[1] == "True", pynput_trans_button(parts[2]))
            elif parts[2].startswith("Key"):
                record = KeyboardClickRecord(delay, parts[1] == "True", pynput_trans_key(parts[2]))
            else:
                if parts[2].startswith("\\") or parts[2].startswith("<"):
                    logging.error(f"不支持的按键：{parts[2]}")
                    return False
                record = KeyboardClickRecord(delay, parts[1] == "True", parts[2])
            self._add_record(record)
        return True

    # 开始监听
    def on_start(self):
        self._last_operation_time = time.time()
        self._last_pos = mouse_ctrl.position
        self._add_record(MoveRecord(0.1, self._last_pos[0], self._last_pos[1]))

    # 结束监听
    def on_stop(self):
        # 将最后一次按触发键的记录替换为鼠标坐标记录
        rec = self._records.pop(-1)
        # 记录最后时间间隔
        self._add_record(MoveRecord(rec.delay, mouse_ctrl.position[0], mouse_ctrl.position[1]))

    # 鼠标移动
    def on_move(self, x: int, y: int):
        if self._last_pos == (x, y):
            return
        self._add_record(MoveRecord(self._delay(), x, y))
        self._last_pos = (x, y)

    # 鼠标点击
    def on_click(self, button: mouse.Button, pressed):
        self._add_record(MouseClickRecord(self._delay(), pressed, button))

    # 键盘按下
    def on_press(self, key: keyboard.Key):
        key = pynput_standardize_key(key)
        self._add_record(KeyboardClickRecord(self._delay(), True, key))

    # 键盘抬起
    def on_release(self, key: keyboard.Key):
        key = pynput_standardize_key(key)
        self._add_record(KeyboardClickRecord(self._delay(), False, key))

    # 保留当前宏
    def on_retain(self):
        for rec in self._records:
            rec.on_retain()

    def imitate(self, interrupt_key, batch=False) -> bool:
        if not batch:
            AudioMgr.play(AudioMgr.SOUND_START_IMITATE)

        def _on_key_release(key):
            key = pynput_key_to_string(key)
            if key == interrupt_key:
                nonlocal interrupted
                interrupted = True
                return False
        interrupted = False
        # 执行宏时再次按触发按键终止模拟
        interrupt_listener = keyboard.Listener(on_release=_on_key_release)
        in_th = Thread(target=interrupt_listener.start)
        in_th.start()

        last_move_record = None
        for rec in self._records:
            if interrupted:
                logging.info("终止模拟")
                break
            if not isinstance(rec, MoveRecord):
                rec.imitate()
                continue
            if not self.relative_mode:
                rec.imitate()
                continue
            if last_move_record:    # 第一个点时，相对模式下即为鼠标当前位置，不用模式
                rec.imitate(last_move_record)
            last_move_record = rec
        interrupt_listener.join() if interrupted else interrupt_listener.stop()
        in_th.join()
        if not batch:
            AudioMgr.play(AudioMgr.SOUND_STOP_IMITATE)
        return not interrupted

    # 删除对应文件
    def remove_file(self):
        if os.path.exists(self._file):
            os.remove(self._file)

    # 将宏数据存储到dict中
    def to_dict(self):
        file_path = os.path.join(GlobalConfig.MACRO_DIR, self.name + ".macro")
        self._save(file_path)
        return {
            "hot_key": self.hot_key,
            "file_path": file_path,
            "desc": self.desc
        }

    # 从dict中解析宏数据
    def from_dict(self, data: dict):
        self._file = data["file_path"]
        self._hot_key = data["hot_key"]
        self._desc = data.get("desc", "")
        return self._load()
