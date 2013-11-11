import time
from AVA1.AVA1_a.Watchman import Watchman
from AVA1.AVA1_b.GraphKnot import GraphKnot


__author__ = 'me'

if __name__ == '__main__':
    filename = './AVA1_a/json_data'
    topology_filename = './AVA1_b/topology'

    for num in range(8):
        l = GraphKnot(num, filename, topology_filename)
        l.start()

    time.sleep(0.5)
    watchman = Watchman(filename)
    watchman.user_interface()
