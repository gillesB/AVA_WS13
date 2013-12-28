import time
from AVA3.AVA3b.EdgeChasingWatchman import EdgeChasingWatchman
from AVA3.AVA3c.MisraForkKnot import MisraForkKnot
from AVA3.AVA3c.MisraPhiloKnot import MisraPhiloKnot


__author__ = 'me'

'''
Startet den dritten Teil der dritten Uebung. Erstellt 5 Chandy/Misra Philosophen Knoten Prozesse (MisraPhiloKnot) und
5 Chandy/Misra Gabel Knoten (MisraForkKnot). Diese sind in einem Kreis angeordnet und kommen abwechselnd vor.
'''
if __name__ == '__main__':
    filename = './json_data'
    topology_filename = './topology'

    for num in range(10):
        if num % 2 == 0:
            if num == 0:
                #startet mit 2 Gabeln
                l = MisraPhiloKnot(num, filename, topology_filename, 2)
            elif num == 8:
                #startet ohne Gabeln
                l = MisraPhiloKnot(num, filename, topology_filename, 0)
            else:
                #startet mit einer Gabel
                l = MisraPhiloKnot(num, filename, topology_filename)
        else:
            l = MisraForkKnot(num, filename, topology_filename)
        l.start()
