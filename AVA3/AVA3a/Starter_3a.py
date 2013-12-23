import time
from AVA3.AVA3a.TokenWatchman import TokenWatchman
from AVA3.AVA3a.TokenForkKnot import TokenForkKnot
from AVA3.AVA3a.TokenPhilosopherKnot import TokenPhilosopherKnot


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
            l = TokenPhilosopherKnot(num, filename, topology_filename)
        else:
            l = TokenForkKnot(num, filename, topology_filename)
        l.start()

    time.sleep(0.5)
    watchman = TokenWatchman(filename)
    watchman.user_interface()
