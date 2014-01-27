import time
import cPickle
from AVA1.AVA1_a.Watchman import Watchman
from CodeBase.Message import Message

__author__ = 'me'


class TimeZoneWatchman(Watchman):
    '''
    Ein Terminierungsbeobachter der nach dem Zeitzonenverfahren funktioniert.
    '''
    def __init__(self, topology_filename):
        Watchman.__init__(self, topology_filename)
        self._check_message = Message('terminationCheck', 'Are you ready?', True)

    def check_termination(self):
        '''
        Sendet checkTermination Nachrichten an alle Knotenund erhaelt eine Antwort s und r von diesen.
        * addiert s und r zu S bzw. R auf
        * ueberprueft ob alle Prozesse in der gleichen Zeitzone sind
        '''
        S = 0
        R = 0
        failed = True
        timezones = set()
        for localKnot_id in self._ips_and_ports.keys():
            for i in range(3):
                try:
                    self.logger.info(
                        "Sending Termination Check Message to " + str(localKnot_id) + ". Try: " + str(i + 1))
                    s, r = self.send_check_message(timezones, localKnot_id)
                    S += s
                    R += r
                    failed = False
                    break
                except:
                    self.logger.error('Error while receiving terminationCheck.', exc_info=1)
                    failed = True
            if failed:
                self.logger.error("I give up sending Termination Check Message to " + str(localKnot_id) + ".")
                break
            time.sleep(1)

        if failed:
            self.logger.error("Fehler bei Terminierungstest.")
        elif len(timezones) != 1:
            self.logger.info("Unterschiedliche Zeitzonen. Algo ist NICHT terminiert.")
        elif S == R:
            self.logger.info("Algo ist terminiert. (" + str(S) + ", " + str(R) + ")")
        else:
            self.logger.info("Algo ist NICHT terminiert. (" + str(S) + ", " + str(R) + ")")

    def send_check_message(self, timezones, localKnot_id):
        '''
        * Sende eine terminationCheck-Nachricht an einen KontoKnoten
        * Verarbeite seine Antwort und gebe sein s und r zurueck
        '''
        socket_o = self.send_message_to_id(localKnot_id, self._check_message)
        if socket_o:
            data = socket_o.recv(1024)
            if data:
                statistics_message = cPickle.loads(data)
                timezones.add(statistics_message.time_zone)
                self.logger.info("Received the message amounts of " + str(localKnot_id) + ". (" + str(
                    statistics_message.messages_sent) + ", " + str(statistics_message.messages_received) + ")")
                return statistics_message.messages_sent, statistics_message.messages_received
            else:
                return 0, 0

    def user_interface(self):
        '''
        Schreibt Nachrichten an den Benutzer und empfaengt Befehle von diesem.
        * sende init Nachricht an Knoten mit ID
        * sende checkTermination Nachricht an alle Knoten
        '''
        while True:
            print 'You can: send init message (init <ID>); check termination (check)'
            user_input = raw_input('$ ').split(' ')
            command = user_input[0]
            if command == 'init' or command == 'i':
                self.send_message_to_id(user_input[1], self._init_message)
            elif command == 'check' or command == 'c':
                self.check_termination()
            else:
                print 'command not known'
            time.sleep(0.5)