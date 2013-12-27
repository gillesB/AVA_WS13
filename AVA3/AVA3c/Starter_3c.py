import time
from AVA3.AVA3b.EdgeChasingWatchman import EdgeChasingWatchman
from AVA3.AVA3c.MisraForkKnot import MisraForkKnot
from AVA3.AVA3c.MisraPhiloKnot import MisraPhiloKnot


__author__ = 'me'

'''
Startet den zweiten Teil der ersten Uebung. Erstellt 8 Graphviz Knoten Prozesse (Graphknots) und
einen Beobachter (Watchman).
'''
if __name__ == '__main__':
    filename = './json_data'
    topology_filename = './topology'

    for num in range(10):
        if num % 2 == 0:
            l = MisraPhiloKnot(num, filename, topology_filename)
        else:
            l = MisraForkKnot(num, filename, topology_filename)
        l.start()

    time.sleep(0.5)
    watchman = EdgeChasingWatchman(filename)
    watchman.user_interface()
