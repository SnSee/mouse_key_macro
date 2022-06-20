import logging
from PyQt5.QtCore import QObject, pyqtSignal


class QLogHandler(logging.Handler, QObject):
    new_message = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record) -> None:
        # noinspection all
        self.new_message.emit(self.format(record))


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(QLogHandler())
    logging.error("qt handler test")
