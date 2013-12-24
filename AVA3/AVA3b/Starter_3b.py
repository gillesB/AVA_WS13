import time
from AVA3.AVA3b.EdgeChasingForkKnot import EdgeChasingForkKnot
from AVA3.AVA3b.EdgeChasingPhiloKnot import EdgeChasingPhiloKnot
from AVA3.AVA3b.EdgeChasingWatchman import EdgeChasingWatchman


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
            l = EdgeChasingPhiloKnot(num, filename, topology_filename)
        else:
            l = EdgeChasingForkKnot(num, filename, topology_filename)
        l.start()

    time.sleep(0.5)
    watchman = EdgeChasingWatchman(filename)
    watchman.user_interface()
