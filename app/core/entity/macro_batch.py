from audio.audio_manager import AudioMgr
from globals.name import Name


class MacroBatch:
    def __init__(self, name: str):
        self.name = name
        self._hot_key = None
        self._desc = ""
        self._macros = []   # [[Macro, times, relative]]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        Name.update_index(name)
        self._name = name

    @property
    def hot_key(self):
        return self._hot_key

    @hot_key.setter
    def hot_key(self, key: str):
        self._hot_key = key

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, desc):
        self._desc = desc

    @property
    def macros(self):
        return self._macros

    def add_macro(self, macro, times, relative):
        self._macros.append([macro, times, relative])

    def del_macro(self, index: int):
        return self._macros.pop(index)

    def clear(self):
        self._macros.clear()
        
    def has_macro(self, macro_name: str):
        for macro in self._macros:
            if macro[0].name == macro_name:
                return True
        return False

    def set_imitate_times(self, macro_name: str, times: int):
        for ml in self._macros:
            if ml[0].name == macro_name:
                ml[1] = times
                return
        assert False

    def set_relative_mode(self, macro_name: str, relative: bool):
        for ml in self._macros:
            if ml[0].name == macro_name:
                ml[2] = relative
                return
        assert False

    def imitate(self):
        AudioMgr.play(AudioMgr.SOUND_START_IMITATE)
        for macro, times, relative in self._macros:
            self_mode, macro.relative_mode = macro.relative_mode, relative
            keep_imitate = True    # 是否继续模拟
            for _ in range(times):
                if not macro.imitate(self.hot_key, batch=True):
                    keep_imitate = False
                    break
            # 恢复宏自身的相对模式
            macro.relative_mode = self_mode
            if not keep_imitate:
                break
        AudioMgr.play(AudioMgr.SOUND_STOP_IMITATE)

    # 将宏数据存储到dict中
    def to_dict(self):
        return {
            "hot_key": self.hot_key,
            "macros": [
                {
                    "name": m[0].name,
                    "times": m[1],
                    "relative": m[2]
                } for m in self.macros
            ],
            "desc": self.desc
        }

    # 从dict中解析宏数据
    def from_dict(self, data: dict, macros: dict):
        self._hot_key = data["hot_key"]
        self._desc = data["desc"]
        for macro in data["macros"]:
            self.add_macro(macros[macro["name"]], macro["times"], macro["relative"])
