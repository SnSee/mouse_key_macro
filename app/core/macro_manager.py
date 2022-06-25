import os
import json
import logging
from threading import Thread, Lock
from pynput import mouse, keyboard

from globals.config import GlobalConfig
from audio.audio_manager import AudioMgr
from utils.key_transfer import pynput_key_to_string
from entity.macro import Macro
from entity.macro_batch import MacroBatch


class MacroManager:
    LISTEN_EXIT_RECORD = 0
    LISTEN_EXIT_IMITATE = 1

    @staticmethod
    def get_sound_enabled():
        return AudioMgr.enabled
    
    # 是否播放声音
    @staticmethod
    def set_sound_enabled(play: bool):
        AudioMgr.enabled = play

    # switch_key: 触发录制快捷键
    # call_back: 结束录制时回调函数
    def __init__(self, switch_key="", call_back=None):
        self._listener = None                   # 触发按键监听器
        self._recording = False                 # 录制状态
        self._imitating = False                 # 正在执行宏
        self._macro = None                      # 正在录制的宏
        self._all_macros = {}                   # 所有宏，{name, Macro}
        self._macro_names = []                  # 宏名，表示宏在表格中顺序
        self._batches = {}                      # 宏组，{name, MacroBatch}
        self._batch_names = []                  # 宏组名，表示宏在表格中顺序
        self._switch_key = switch_key           # 开始/暂停录制快捷键
        self._callback = call_back              # 结束录制回调
        self._hot_keys = set()                  # 所有快捷键
        self._lock = Lock()                     # TODO: 是否需要用锁保证监听回调顺序？
        self.load_from_file()

    @staticmethod
    def config():
        return GlobalConfig

    @property
    def switch_key(self):
        return self._switch_key

    @switch_key.setter
    def switch_key(self, key):
        logging.info(f"已设置触发录制按键: {key}")
        self._switch_key = key

    @property
    def macro_names(self):
        return self._macro_names

    @property
    def batch_names(self):
        return self._batch_names

    @property
    def all_macros(self):
        return self._all_macros

    def _add_hot_key(self, key):
        if key:
            self._hot_keys.add(key)

    def _replace_hot_key(self, old_key, new_key):
        if old_key in self._hot_keys:
            self._hot_keys.remove(old_key)
        self._add_hot_key(new_key)

    # 鼠标移动回调
    def _on_move(self, x, y):
        if not self._recording:
            return
        self._macro.on_move(x, y)

    # 鼠标按下/松开回调
    def _on_click(self, _, __, button, pressed):
        if not self._recording:
            return
        self._macro.on_click(button, pressed)

    # 键盘按下回调
    def _on_press(self, key):
        if not self._recording:
            return
        self._macro.on_press(key)

    # 键盘松开回调
    def _on_release(self, key):
        if not self._recording:
            return
        key_text = pynput_key_to_string(key)
        if key_text == self._switch_key:
            return self._stop_record()
        self._macro.on_release(key)

    # 监听鼠标
    def _monitor_mouse(self):
        self._ml = mouse.Listener(on_move=self._on_move, on_click=self._on_click)
        self._ml.start()
        self._ml.join()

    # 监听键盘
    def _monitor_keyboard(self):
        self._kbl = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._kbl.start()
        self._kbl.join()

    # 开始录制
    def _start_record(self):
        AudioMgr.play(AudioMgr.SOUND_START_RECORD)
        logging.info("开始录制")
        self._recording = True
        self._macro = Macro()
        self._macro.on_start()
        mouse_th = Thread(target=self._monitor_mouse)
        keyboard_th = Thread(target=self._monitor_keyboard)
        mouse_th.start()
        keyboard_th.start()
        mouse_th.join()
        keyboard_th.join()

    # 停止录制
    def _stop_record(self, forced=False):
        AudioMgr.play(AudioMgr.SOUND_STOP_RECORD)
        logging.info("停止录制")
        self._recording = False
        self._ml.stop()
        self._kbl.stop()
        self._macro.on_stop()
        if self._callback and not forced:
            self._callback()

    # 打包成dict，方便使用json写入文件
    def _to_dict(self):
        macro_configs = {name: macro.to_dict() for name, macro in self._all_macros.items()}
        batches = {name: batch.to_dict() for name, batch in self._batches.items()}
        json_dict = {
            "switch_key": self.switch_key,
            "macro_names": self._macro_names,
            "macros": macro_configs,
            "batch_names": self._batch_names,
            "batches": batches
        }
        json_dict.update(GlobalConfig.to_dict())
        json_dict.update(AudioMgr.to_dict())
        return json_dict

    def _from_dict(self, json_dict: dict):
        macros = json_dict.get("macros", {})
        for macro_name in json_dict.get("macro_names", []):
            self._macro = Macro(macro_name)
            if self._macro.from_dict(macros[macro_name]):
                self.retain_current()
        batches = json_dict.get("batches", {})
        for mb_name in json_dict.get("batch_names", []):
            batch = MacroBatch(mb_name)
            batch.from_dict(batches[mb_name], self._all_macros)
            self._add_hot_key(batch.hot_key)
            self.add_batch(mb_name, batch)
        self.switch_key = json_dict.get("switch_key", "")
        GlobalConfig.from_dict(json_dict)
        AudioMgr.from_dict(json_dict)

    # 设置结束录制回调
    def set_callback(self, callback):
        self._callback = callback

    # 设置触发快捷键
    def set_hot_key(self, macro_name: str, hot_key: str):
        if not self.valid_hot_key(hot_key):
            return False
        macro = self._all_macros[macro_name]
        self._replace_hot_key(macro.hot_key, hot_key)
        macro.hot_key = hot_key
        desc = "设置" if hot_key else "清空"
        logging.info(f"已{desc}宏 {macro_name} 快捷键{':' if hot_key else ''} {hot_key}")
        return True

    def set_macro_relative(self, macro_name: str, relative: bool):
        self._all_macros[macro_name].relative_mode = relative

    def set_macro_desc(self, macro_name: str, desc: str):
        self._all_macros[macro_name].desc = desc

    # 设置宏组快捷键
    def set_batch_hot_key(self, batch_name: str, hot_key: str):
        if not self.valid_hot_key(hot_key):
            return False
        mb = self._batches.get(batch_name, None)
        if not mb:
            logging.warning("宏名尚未设置")
            return False
        if mb.hot_key == hot_key:
            return True
        self._replace_hot_key(mb.hot_key, hot_key)
        mb.hot_key = hot_key
        desc = "设置" if hot_key else "清空"
        logging.info(f"已{desc}宏组 {batch_name} 快捷键{':' if hot_key else ''} {hot_key}")
        return True

    # 设置宏组描述信息
    def set_batch_desc(self, batch_name: str, desc: str):
        mb = self._batches.get(batch_name, None)
        if not mb:
            logging.warning("宏名尚未设置")
            return False
        mb.desc = desc
        return True

    # 重命名宏
    def rename_macro(self, index: int, new_name: str):
        if not new_name:
            logging.error("宏名不能为空")
            return False
        if not self.valid_macro_name(new_name):
            return False
        old_name = self._macro_names[index]
        macro = self._all_macros.get(old_name, None)
        assert macro
        del self._all_macros[old_name]
        macro.name = new_name
        self._all_macros[new_name] = macro
        self._macro_names[index] = new_name
        logging.info(f"宏 {old_name} 已重命名为 {new_name}")
        return True

    # 重命名宏组
    def rename_batch(self, index: int, new_name: str):
        if not new_name:
            logging.error("宏名不能为空")
            return False
        if not self.valid_batch_name(new_name):
            return False
        old_name = self._batch_names[index]
        batch = self._batches[old_name]
        del self._batches[old_name]
        batch.name = new_name
        self._batches[new_name] = batch
        self._batch_names[index] = new_name
        logging.info(f"宏组 {old_name} 已重命名为 {new_name}")
        return True

    # 保留当前宏
    def retain_current(self, name="", hot_key=""):
        if name:
            self._macro.name = name
        assert self._macro.name
        assert self._macro.name not in self._all_macros
        if hot_key:
            self._macro.hot_key = hot_key
        self._macro.on_retain()
        self._all_macros[self._macro.name] = self._macro
        self._macro_names.append(self._macro.name)
        self.set_hot_key(self._macro.name, self._macro.hot_key)
        logging.info(f"宏 {self._macro.name} 已记录")

    # 删除宏
    def del_macro(self, name: str):
        # 如果宏在宏组中需要先删除宏组
        batches = []
        for mb in self._batches.values():
            if mb.has_macro(name):
                batches.append(mb.name)
        if batches:
            logging.warning(f"需要先删除宏组{batches}才能删除宏")
            return False
        macro = self._all_macros.get(name, None)
        assert macro
        if macro.hot_key in self._hot_keys:
            self._hot_keys.remove(macro.hot_key)
        del self._all_macros[name]
        self._macro_names.remove(name)
        macro.remove_file()
        logging.info(f"宏 {name} 已被删除")
        return True

    # 新建宏组
    def add_batch(self, name: str, batch: MacroBatch = None):
        if name in self._batches:
            logging.error("宏组名称已被占用")
            return False
        self._batches[name] = batch if batch else MacroBatch(name)
        self._batch_names.append(name)
        logging.info(f"已添加宏组 {name}")
        return True

    # 删除宏组
    def del_batch(self, name: str):
        if name in self._batches:
            del self._batches[name]
            self._batch_names.remove(name)
            logging.info(f"宏组 {name} 已删除")

    # 向宏组添加宏
    def add_macro_to_batch(self, batch_name: str, macro_name: str, times, relative):
        mb = self._batches[batch_name]
        mb.add_macro(self._all_macros[macro_name], times, relative)
        logging.info(f"已向宏组 {batch_name} 添加宏: {macro_name}")

    # 从宏组中删除宏
    def del_macro_from_batch(self, batch_name: str, index: int):
        if batch_name not in self._batches:
            return
        macro = self._batches[batch_name].del_macro(index)
        logging.info(f"已从宏组 {batch_name} 删除宏: {macro.name}")

    # 清空宏组中的宏
    def clear_batch_macros(self, batch_name):
        self._batches[batch_name].clear()

    # 获取宏名
    def get_macro_name(self, index: int):
        return self._macro_names[index]

    # 获取宏组名
    def get_batch_name(self, index: int):
        return self._batch_names[index]

    def get_batch(self, name: str):
        return self._batches.get(name, None)

    # 是否存在宏
    def has_macro_name(self, name: str):
        return name in self._all_macros
    
    # 宏名是否有效
    def valid_macro_name(self, name: str):
        if name in self._all_macros:
            logging.warning(f"宏名 {name} 已被占用")
            return False
        return True

    # 宏组名是否有效
    def valid_batch_name(self, name: str):
        if name in self._batches:
            logging.warning(f"宏组名 {name} 已被占用")
            return False
        return True

    def valid_hot_key(self, hot_key: str):
        if hot_key in self._hot_keys:
            logging.warning(f"触发按键 {hot_key} 已被占用")
            return False
        return True

    # 开启监听，触发录制或模拟后退出
    def listen_once(self):
        to_record = False   # 为True表示开始录制宏
        hot_key = None

        def _on_key_release(key):
            key = pynput_key_to_string(key)
            if key == self._switch_key:
                nonlocal to_record
                to_record = True
                return False
            if key in self._hot_keys:
                nonlocal hot_key
                hot_key = key
                return False
        self._listener = keyboard.Listener(on_release=_on_key_release)
        logging.info(f"监听中, 按触发按键开始录制或模拟按键开始模拟")
        self._listener.start()
        self._listener.join()
        if to_record:
            self._start_record()
            return self.LISTEN_EXIT_RECORD
        if hot_key:
            self.imitate(hot_key)
            # 如果是模拟，模拟完继续监听
            return self.LISTEN_EXIT_IMITATE
        return False    # 监听不是由快捷键触发的，由stop_listen触发

    # 持续监听，触发录制后退出，触发模拟不退出
    def keep_imitate_listen(self):
        while self.listen_once() == self.LISTEN_EXIT_IMITATE:
            pass

    # 停止监听，需要通过其他线程调用
    def stop_listen(self):
        if self._listener:
            self._listener.stop()
        if self._recording:
            self._stop_record(forced=True)

    # 执行指定宏，如果有快捷键相同的，只执行排在最前面的
    # 不是线程安全的，不要在多个线程里同时调用
    def imitate(self, hot_key):
        if hot_key not in self._hot_keys:
            return
        for macro in self._all_macros.values():
            if macro.hot_key == hot_key:
                logging.info(f"{macro.name} 开始模拟")
                self._imitating = True
                macro.imitate(hot_key)
                self._imitating = False
                logging.info(f"{macro.name} 结束模拟")
                return
        for batch in self._batches.values():
            if batch.hot_key == hot_key:
                logging.info(f"{batch.name} 开始模拟")
                self._imitating = True
                batch.imitate()
                self._imitating = False
                logging.info(f"{batch.name} 结束模拟")
                return
        assert False

    # 在__del__中调用会有问题，所以由使用者手动调用
    def save_to_file(self):
        # 保存所有宏
        if not os.path.exists(GlobalConfig.MACRO_DIR):
            os.mkdir(GlobalConfig.MACRO_DIR)
        json_file = os.path.join(GlobalConfig.MACRO_DIR, GlobalConfig.MACRO_CONFIG)
        with open(json_file, "w") as fj:
            fj.write(json.dumps(self._to_dict(), indent=2))

    def load_from_file(self):
        json_file = os.path.join(GlobalConfig.MACRO_DIR, GlobalConfig.MACRO_CONFIG)
        json_dict = {}
        if os.path.exists(json_file):
            with open(json_file) as fj:
                json_dict = json.load(fj)
        self._from_dict(json_dict)


MacroMgr = MacroManager()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # key_ctrl.press("1")
