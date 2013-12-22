from sets import Set
import time
import cPickle
from AVA1.AVA1_a.Watchman import Watchman
from CodeBase.Message import Message

__author__ = 'me'


class TimeZoneWatchman(Watchman):

    def __init__(self, topology_filename):
        Watchman.__init__(self, topology_filename)
        self._check_message = Message('terminationCheck', 'Are you ready?', True)

    def check_termination(self):
        '''
        Sendet checkTermination Nachrichten an alle Knoten.
        '''
        S = 0
        R = 0
        for localKnot_id in self._ips_and_ports.keys():
            socket = self.send_message_to_id(localKnot_id, self._check_message)
            timezones = Set()
            if socket:
                try:
                    data = socket.recv(1024)
                    if data:
                        statistics_message = cPickle.loads(data)
                        S += statistics_message.messages_sent
                        R += statistics_message.messages_received
                        timezones.add(statistics_message.time_zone)
                except:
                    self.logger.error('Error while receiving terminationCheck.', exc_info=1)
                    S = -1
                    break
            else:
                S = -1
                break
        if S == -1:
            self.logger.error("Fehler bei Terminierungstest.")
        elif len(timezones) != 1:
            self.logger.info("Unterschiedliche Zeitzonen. Algo ist NICHT terminiert.")
        elif S == R:
            self.logger.info("Algo ist terminiert.")
        else:
            self.logger.info("Algo ist NICHT terminiert.")

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