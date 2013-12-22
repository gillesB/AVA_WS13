import time
from AVA2.AVA2_b.TimeZoneKontoKnot import TimeZoneKontoKnot
from AVA2.AVA2_b.TimeZoneWatchman import TimeZoneWatchman


__author__ = 'me'

if __name__ == '__main__':
    filename = './AVA2_a/json_data'

    for num in range(8):
        l = TimeZoneKontoKnot(num, filename)
        l.start()

    time.sleep(0.5)
    watchman = TimeZoneWatchman(filename)
    watchman.user_interface()
