import time


def waste_time(duration):
    ct = time.time()
    while time.time() - ct < duration:
        pass
