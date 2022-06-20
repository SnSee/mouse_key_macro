import threading
import winsound
import pyttsx3

_SOUND_DIR = "./sounds/"


class _AudioManager:

    SOUND_START_RECORD = _SOUND_DIR + "start_record.mp3"
    SOUND_STOP_RECORD = _SOUND_DIR + "stop_record.mp3"
    SOUND_START_IMITATE = _SOUND_DIR + "start_imitate.mp3"
    SOUND_STOP_IMITATE = _SOUND_DIR + "stop_imitate.mp3"

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


AudioMgr = _AudioManager()
