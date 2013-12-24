import time
from CodeBase.AbstractWatchman import AbstractWatchman
from CodeBase.Message import Message

__author__ = 'me'

class EdgeChasingWatchman(AbstractWatchman):
    '''
    Ein einfacher Beobachter, der von einem Benutzer gesteuert werden kann. Er kann zwei Arten Nachrichten an die Knoten
    versenden. Init Nachrichten und Suicide Nachrichten.
    '''

    def __init__(self, topology_filename):
        AbstractWatchman.__init__(self, topology_filename)
        self._check_deadlock_message = Message('checkDeadlock', 'Is this the end of the beginning?', True)
        self._kill_message = Message('suicide', 'Or the beginning of the end?', True)

    def terminate_all(self):
        '''
        Sendet Suicide Nachrichten an alle Knoten.
        '''
        for localKnot_id in self._ips_and_ports.keys():
            self.send_message_to_id(localKnot_id, self.__kill_message)

    def user_interface(self):
        '''
        Schreibt Nachrichten an den Benutzer und empfaengt Befehle von diesem.
        * sende init Nachricht an Knoten mit ID
        * sende suicide Nachricht an Knoten mit ID
        * sende suicide Nachricht an alle Knoten
        '''
        while True:
            print 'You can: send check_deadlock message (check_deadlock <ID>); kill knot (kill <ID>); kill all knots (killAll)'
            user_input = raw_input('$ ').split(' ')
            command = user_input[0]
            if command == 'check_deadlock' or command == 'c':
                self.send_message_to_id(user_input[1], self._check_deadlock_message)
            elif command == 'kill' or command == 'k':
                self.send_message_to_id(user_input[1], self.__kill_message)
            elif command == 'killAll' or command == 'ka':
                self.terminate_all()
            else:
                print 'command not known'
            time.sleep(0.5)