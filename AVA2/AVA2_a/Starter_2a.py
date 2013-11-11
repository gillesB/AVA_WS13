import time
from AVA1.AVA1_a.Watchman import Watchman
from AVA2.AVA2_a.KontoKnot import KontoKnot


__author__ = 'me'

if __name__ == '__main__':
    filename = './AVA2_a/json_data'

    for num in range(8):
        l = KontoKnot(num, filename)
        l.start()

    time.sleep(0.5)
    watchman = Watchman(filename)
    watchman.user_interface()
