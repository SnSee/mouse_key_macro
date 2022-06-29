import logging

_level_to_string = {
    logging.DEBUG: "Debug",
    logging.INFO: "Info",
    logging.WARNING: "Warning",
    logging.ERROR: "Error"
}

_string_to_level = {v: k for k, v in _level_to_string.items()}


def level_to_string(level):
    return _level_to_string.get(level, None)


def string_to_level(level_str):
    return _string_to_level.get(level_str, None)
