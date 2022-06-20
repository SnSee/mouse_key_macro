import re

_NO_NAME = "未命名"


class _Name:
    def __init__(self):
        self._index = 1

    def default_name(self):
        name = f"{_NO_NAME}{self._index}"
        self._index += 1
        return name

    def update_index(self, name: str):
        ret = re.match(rf"{_NO_NAME}(\d+)", name)
        if not ret:
            return
        self._index = max(self._index, int(ret.group(1)) + 1)


Name = _Name()
