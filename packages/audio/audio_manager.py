import os
import threading
import winsound
import pyttsx3

_SOUND_DIR = os.path.join(os.path.dirname(__file__), "sounds")


class _AudioManager:

    SOUND_START_RECORD = os.path.join(_SOUND_DIR, "start_record.mp3")
    SOUND_STOP_RECORD = os.path.join(_SOUND_DIR, "stop_record.mp3")
    SOUND_START_IMITATE = os.path.join(_SOUND_DIR, "start_imitate.mp3")
    SOUND_STOP_IMITATE = os.path.join(_SOUND_DIR, "stop_imitate.mp3")

    def __init__(self):
        self._engine = pyttsx3.init(debug=True)
        self._thread = None
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        self._enabled = enabled

    def _play(self, file: str):
        if self._enabled:
            winsound.PlaySound(file, winsound.SND_FILENAME)

    def play(self, file: str):
        self._thread = threading.Thread(target=self._play, args=[file])
        self._thread.start()

    def join(self):
        if self._thread:
            self._thread.join()

    def save_to_file(self, text: str, file: str):
        self._engine.save_to_file(text, file)
        self._engine.runAndWait()

    def to_dict(self):
        return {"enable_sound": self.enabled}

    def from_dict(self, data: dict):
        self.enabled = data.get("enable_sound", False)


AudioMgr = _AudioManager()
