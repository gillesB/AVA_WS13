from LocalKnot import LocalKnot
from Watchman import Watchman
import time

__author__ = 'me'

if __name__ == '__main__':
    filename = './json_data'

    for num in range(8):
        l = LocalKnot(num, filename)
        l.start()

    time.sleep(1)
    watchman = Watchman(filename)
    watchman.user_interface()
