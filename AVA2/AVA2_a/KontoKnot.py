from random import SystemRandom
from CodeBase.AbstractKnot import AbstractKnot
from CodeBase.Message import Message

__author__ = 'me'


class KontoKnot(AbstractKnot):
    MAX = 100
    MAX_DIFF = 10
    MAX_N = 4

    def __init__(self, ID, connections_filename):
        super(KontoKnot, self).__init__(ID, connections_filename)
        #init message counters
        #r aus der Angabe
        self._amount_messages_received = 0
        #s aus der Angabe
        self._amount_messages_sent = 0

        self.kontostand = 0

    def run(self):
        self.init_start_konto_betrag()
        self.read_connections_and_open_port()
        while True:
            self.receive_messages()

    def init_start_konto_betrag(self):
        self.kontostand = self._system_random.randint(KontoKnot.MAX / 2, KontoKnot.MAX)
        self.logger.info('Der Startkontostand betraegt: ' + str(self.kontostand))

    def process_received_message(self, connection, message):
        if message.getAction() == 'konto_abzug':
            #r um 1 erhoehen
            self._amount_messages_received += 1
            konto_abzug = message.getMessage()
            self.eigener_konto_abzug(konto_abzug)

            self.send_konto_abzuege()
        elif message.getAction() == 'init':
            self.send_konto_abzuege()

    def eigener_konto_abzug(self, value):
        self.kontostand -= value
        self.logger.info('Der neue Kontostand betraegt: ' + str(self.kontostand))

    def send_konto_abzuege(self):
        if self.kontostand > 0:
            konto_abzug = self._system_random.randint(1, KontoKnot.MAX_DIFF)

            amount_neighbours = self._system_random.randint(1, KontoKnot.MAX_N)
            self.choose_new_neighbours(amount_neighbours)

            konto_abzug_message = Message('konto_abzug', konto_abzug, sender=self._ID)
            self.logger.info("Sende Nachrichten an: " + str(self._neighbours.keys()))
            for neighbourID in self._neighbours.keys():
                #s um 1 erhoehen
                self._amount_messages_sent += 1
                self.send_message_to_id(konto_abzug_message, neighbourID)


