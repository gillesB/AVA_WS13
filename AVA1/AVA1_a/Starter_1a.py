import time
from AVA1.AVA1_a.LocalKnot import LocalKnot
from AVA1.AVA1_a.Watchman import Watchman


__author__ = 'me'

'''
Startet den ersten Teil der ersten Uebung. Erstellt 8 Knoten Prozesse (LocalKnots) und einen Beobachter (Watchman).
'''
if __name__ == '__main__':
    filename = './AVA1_a/json_data'

    for num in range(8):
        l = LocalKnot(num, filename)
        l.start()

    time.sleep(0.5)
    watchman = Watchman(filename)
    watchman.user_interface()
