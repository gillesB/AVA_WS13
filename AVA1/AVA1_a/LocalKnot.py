import random
import sys

from CodeBase.Message import Message
from CodeBase.AbstractKnot import AbstractKnot


__author__ = 'me'


class LocalKnot(AbstractKnot):
    '''
    Ein einfacher Knoten, der sobald er eine Nachricht empfaengt, seine ID, einmalig, an seine Nachbarn versendet.
    '''

    def __init__(self, ID, connections_filename):
        super(LocalKnot, self).__init__(ID, connections_filename)

    def run(self):
        '''
        Da der Knoten von der Klasse Process erbt, steht innerhalb von run() die Methoden, die ausgefuehrt werden,
        sobal der Prozess gestartet wurde. Siehe auch: http://docs.python.org/dev/library/multiprocessing.html
        * Initialisiert sich selbst und tritt dann in eine Endlosschleife ein.
        * Wartet auf eine Nachricht
        * Nach dem Empfang der ersten Nachricht, sendet er seine ID zu seinen Nachbarn.
        * (Außer die erste Nachricht war eine suicide-Nachricht, dann ist der Process bereits beendet.)
        '''
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours(3)
        init = True
        while True:
            self.receive_messages()
            if init:
                self.send_id_to_neighbours()
                init = False

    def process_received_message(self, message):
        '''
        Der Knoten stoppt sich selbst, sobald er eine Nachricht mit der Aktion 'suicide' empfaengt.
        Die 'init' Nachricht wird nicht extra verarbeitet, d.h. eine Nachricht mit einer anderen Aktion wuerde auch
        das Versenden der ID an die Nachbarn ausloesen.
        '''
        if message.getAction() == 'suicide':
            sys.exit(0)

    def send_id_to_neighbours(self):
        '''
        Sende die eigene ID an die Nachbarn. Die Nachricht hat die Aktion 'ID' und als Daten die eigene ID.
        '''
        own_id_message = Message("ID", self._ID)
        for neighbourID in self._neighbours.keys():
            self.send_message_to_id(own_id_message, neighbourID)

if __name__ == '__main__':
    '''
    Der Knoten koennte auch als eigenes Skript laufen, das Benutzen der starter Skripte ist allerdings komfortabler.
    '''
    id = sys.argv[1]
    filename = sys.argv[2]
    localKnot = LocalKnot(id, filename)
    localKnot.run()



