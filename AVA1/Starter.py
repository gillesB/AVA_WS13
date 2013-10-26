from LocalKnot import LocalKnot
from Watchman import Watchman
import time

__author__ = 'me'

if __name__ == '__main__':
    filename = './json_data'

    for num in range(7):
        l = LocalKnot(num+1, filename)
        l.start()
        #l.join()

    time.sleep(1)
    watchman = Watchman(filename)
    watchman.read_input_file()
    watchman.send_init_to_zero(1)
