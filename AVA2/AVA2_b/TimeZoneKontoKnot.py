
from AVA2.AVA2_b.StatisticsMessage import StatisticsMessage
from AVA2.AVA2_b.TimeZoneMessage import TimeZoneMessage
from CodeBase.AbstractKnot import AbstractKnot

__author__ = 'me'


class TimeZoneKontoKnot(AbstractKnot):

    MAX = 10000
    MAX_DIFF = 1
    MAX_N = 1

    def __init__(self, ID, connections_filename):
        super(TimeZoneKontoKnot, self).__init__(ID, connections_filename)
        #init message counters
        #r aus der Angabe
        self._amount_messages_received = 0
        #s aus der Angabe
        self._amount_messages_sent = 0

        self.kontostand = 0

        self.__time_zone = 0

        self.__saved_s = -1
        self.__saved_r = -1

    def run(self):
        self.init_start_konto_betrag()
        self.read_connections_and_open_port()
        while True:
            self.receive_messages()

    def init_start_konto_betrag(self):
        self.kontostand = self._system_random.randint(TimeZoneKontoKnot.MAX / 2, TimeZoneKontoKnot.MAX)
        self.logger.info('Der Startkontostand betraegt: ' + str(self.kontostand))

    def process_received_message(self, connection, message):
        if message.getAction() == 'konto_abzug':
            self.process_konto_abzug(connection,message)
        elif message.getAction() == 'init':
            self.send_konto_abzuege()
        elif message.getAction() == "terminationCheck":
            self.__time_zone += 1
            self.send_amount_messages_to_observer(connection, message)

    def process_konto_abzug(self, connection, message):
        if self.__time_zone < message.time_zone:
            self.__saved_s = self._amount_messages_sent
            self.__saved_r = self._amount_messages_received
        #r um 1 erhoehen
        self._amount_messages_received += 1
        konto_abzug = message.getMessage()
        self.eigener_konto_abzug(konto_abzug)

        self.send_konto_abzuege()

    def eigener_konto_abzug(self, value):
        self.kontostand -= value
        self.logger.info('Der neue Kontostand betraegt: ' + str(self.kontostand))

    def send_konto_abzuege(self):
        if self.kontostand > 0 and TimeZoneKontoKnot.MAX_N > 0:
            konto_abzug = self._system_random.randint(1, TimeZoneKontoKnot.MAX_DIFF)

            amount_neighbours = self._system_random.randint(1, TimeZoneKontoKnot.MAX_N)
            self.choose_new_neighbours(amount_neighbours)

            konto_abzug_message = TimeZoneMessage('konto_abzug', konto_abzug, sender=self._ID, time_zone=self.__time_zone)
            self.logger.info("Sende Nachrichten an: " + str(self._neighbours.keys()))
            for neighbourID in self._neighbours.keys():
                #s um 1 erhoehen
                self._amount_messages_sent += 1
                self.send_message_to_id(konto_abzug_message, neighbourID)

    def send_amount_messages_to_observer(self, connection, message):
        if self.__saved_s == -1:
            s = self._amount_messages_sent
            r = self._amount_messages_received
        else:
            s = self.__saved_s
            r = self.__saved_r

        stat_message = StatisticsMessage(self._ID, s, r, self.__time_zone)
        self.send_message_over_socket(connection, stat_message)