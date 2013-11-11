import time
from CodeBase.AbstractWatchman import AbstractWatchman
from CodeBase.Message import Message


__author__ = 'me'


class Watchman(AbstractWatchman):

    def __init__(self, topology_filename):
        AbstractWatchman.__init__(self, topology_filename)
        self.__init_message = Message('init', 'Is this end of the beginning?', True)
        self.__kill_message = Message('suicide', 'Or the beginning of the end?', True)

    def terminate_all(self):
        for localKnot_id in self._ips_and_ports.keys():
            self.send_message_to_id(localKnot_id, self.__kill_message)

    def user_interface(self):
        while True:
            print 'You can: send init message (init <ID>); kill knot (kill <ID>); kill all knots (killAll)'
            user_input = raw_input('$ ').split(' ')
            command = user_input[0]
            if command == 'init' or command == 'i':
                self.send_message_to_id(user_input[1], self.__init_message)
            elif command == 'kill' or command == 'k':
                self.send_message_to_id(user_input[1], self.__kill_message)
            elif command == 'killAll' or command == 'ka':
                self.terminate_all()
            else:
                print 'command not known'
            time.sleep(0.5)


