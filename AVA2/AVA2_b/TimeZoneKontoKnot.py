import socket
import datetime
import cPickle
from AVA2.AVA2_b.StatisticsMessage import StatisticsMessage
from AVA2.AVA2_b.TimeZoneMessage import TimeZoneMessage
from CodeBase.AbstractKnot import AbstractKnot

__author__ = 'me'


class TimeZoneKontoKnot(AbstractKnot):
    '''
    Urspruenglich eine Kopie von KontoKnot wurde erweitert um das Zeitzonenverfahren zu ermoeglichen.
    '''

    MAX = 10000
    MAX_DIFF = 10
    MAX_N = 2

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

        #Anzahl wie haeufig die Kontoabzuge an die Nachbarn versendet werden muessen
        self.amount_abzuege = 0

    def run(self):
        self.init_start_konto_betrag()
        self.read_connections_and_open_port()
        while True:
            self.send_konto_abzuege()
            #self.receive_messages()
            #Der Prozess lauscht nur fuer eine kurze Zeit, ehe wieder gesendet werden kann.
            #Dies fuegt eine kuenstliche Pause ein, so dass nicht alle Knoten gleichzeitig senden
            #und sich nicht gegenseitig blockieren.
            self.wait_and_listen(self._system_random.random() * 0.01)

    def init_start_konto_betrag(self):
        self.kontostand = self._system_random.randint(TimeZoneKontoKnot.MAX / 2, TimeZoneKontoKnot.MAX)
        self.logger.info('Der Startkontostand betraegt: ' + str(self.kontostand))

    def process_received_message(self, connection, message):
        if message.getAction() == 'konto_abzug':
            self.process_konto_abzug(connection,message)
        elif message.getAction() == 'init':
            self.amount_abzuege = 1
            self.send_konto_abzuege()
        elif message.getAction() == "terminationCheck":
            self.__time_zone += 1
            self.send_amount_messages_to_observer(connection, message)

    def process_konto_abzug(self, connection, message):
        if self.__saved_s == -1 and self.__time_zone < message.time_zone:
            self.__saved_s = self._amount_messages_sent
            self.__saved_r = self._amount_messages_received
        #r um 1 erhoehen
        self._amount_messages_received += 1
        konto_abzug = message.getMessage()
        self.eigener_konto_abzug(konto_abzug)

        self.amount_abzuege += 1

    def eigener_konto_abzug(self, value):
        self.kontostand -= value
        self.logger.info('Der neue Kontostand betraegt: ' + str(self.kontostand))

    def send_konto_abzuege(self):
        '''
        Da diese Funktion oefter aufgerufen wird als noetig, muss ueberprueft werden ob ueberhaupt gesendet werden darf.
        Dies geschiet ueber amount_abzuege.
        '''
        if self.kontostand > 0 and self.amount_abzuege > 0:
            konto_abzug = self._system_random.randint(1, TimeZoneKontoKnot.MAX_DIFF)

            amount_neighbours = self._system_random.randint(1, TimeZoneKontoKnot.MAX_N)
            self.choose_new_neighbours(amount_neighbours)

            konto_abzug_message = TimeZoneMessage('konto_abzug', konto_abzug, sender=self._ID, time_zone=self.__time_zone)
            self.logger.info("Sende Nachrichten an: " + str(self._neighbours.keys()))
            for neighbourID in self._neighbours.keys():
                if self.send_message_to_id(konto_abzug_message, neighbourID):
                    #senden erfolgreich: s um 1 erhoehen
                    self._amount_messages_sent += 1

            self.amount_abzuege -= 1

    def send_amount_messages_to_observer(self, connection, message):
        '''
        Sende s und r an den Beobachter. Dies erfolgt ueber den gleichen Socket, der die Ueberpruefungsnachricht
        erhalten hat. Falls durch einen Zeitzonenwechsel s und r zwischengespeichert wurden, so werden diese
        zurueckgesendet.
        '''
        if self.__saved_s == -1:
            s = self._amount_messages_sent
            r = self._amount_messages_received
        else:
            s = self.__saved_s
            r = self.__saved_r

        stat_message = StatisticsMessage(self._ID, s, r, self.__time_zone)
        self.send_message_over_socket(connection, stat_message)
        self.__saved_s = -1
        self.__saved_r = -1

    def wait_and_listen(self, seconds):
        '''
        Wartet eine gewisse Zeit und lauscht waehrendem auf dem offenen Port.
        '''
        now = datetime.datetime.now()
        wait_till = now + datetime.timedelta(0, seconds)
        while seconds > 0.0001:
            #self.logger.info("Still waiting for " + str(seconds))
            try:
                self._listeningSocket.settimeout(seconds)
                connection, addr = self._listeningSocket.accept()
                data = connection.recv(1024)
                if data:
                    message = cPickle.loads(data)
                    self.logger.info("empfangen: " + message.printToString())
                    self.process_received_message(connection, message)
            except socket.timeout:
                pass
            now = datetime.datetime.now()
            seconds = (wait_till - now).total_seconds()
        self._listeningSocket.settimeout(None)