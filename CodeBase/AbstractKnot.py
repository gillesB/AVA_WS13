from abc import abstractmethod
import json
import logging
from logging import FileHandler, Logger
from random import SystemRandom
import socket
import cPickle

import prctl


__author__ = 'me'

from multiprocessing import Process
import os


class AbstractKnot(Process):
    '''
    Ein abstrakter Knoten Prozess. Uebernimmt die einfachsten Aufgaben: Konfigurationsdatei lesen, Port öffnen,
    Nachrichten senden
    '''

    def __init__(self, ID, connections_filename):
        super(AbstractKnot, self).__init__()
        prctl.set_proctitle(self._name + '-' + str(ID))
        self._ID = str(ID)
        self.__connections_filename = connections_filename
        self._ips_and_ports = None
        self.__ip = None
        self.__port = None
        self.__listeningSocket = None
        self._neighbours = {}
        self._system_random = SystemRandom()

        #init logging
        self.logger = Logger(__name__ + '-' + str(ID))
        formatter = logging.Formatter('%(name)s %(levelname)s %(asctime)s: %(message)s')
        filehandler = FileHandler('./Logging/' + self._name + '-' + str(ID) + '.log', 'w')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.NOTSET)
        for hdlr in self.logger.handlers:  # remove all old handlers
            self.logger.removeHandler(hdlr)
        self.logger.addHandler(filehandler)

    def getID(self):
        return self._ID

    def info(self):
        '''
        Der Knoten loggt Informationen ueber sich selbst.
        '''
        info_message = 'module name:' + __name__ + '\n'
        if hasattr(os, 'getppid'):
            info_message += 'parent process:' + str(os.getppid()) + '\n'
        info_message += 'process id:' + str(os.getpid()) + '\n'
        info_message += 'LocalKnot id:' + str(self._ID) + '\n\n'
        self.logger.info(info_message)

    def read_connections_file(self):
        '''
        Liest die Datei mit den Informationen über die Knoten die es ebenfalls im Netzwerk gibt und speichert
        sie in ein dictionary.
        Somit sind die IP und der Port der anderen Knoten mittels ihrerer ID abrufbar.
        Bei der Datei, handelt es sich um eine Json Datei, die mit der richtigen Bibliothek einfach geladen werden kann.
        '''
        json_data = open(self.__connections_filename)
        self._ips_and_ports = json.load(json_data)
        json_data.close()

    def open_port(self):
        '''
        Oeffnet einen Socket auf dem eigenen Serverport auf dem der Prozess hoert und loescht sich selbst aus dem
        dictionary mit den anderen Knoten.
        '''
        self.__ip = self._ips_and_ports[self._ID]["ip"]
        self.__port = self._ips_and_ports[self._ID]["port"]
        del self._ips_and_ports[self._ID]

        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningSocket.bind((self.__ip, self.__port))
        self.__listeningSocket.listen(5)

    def read_connections_and_open_port(self):
        '''
        Fasst die Methoden read_connections_file() und open_port() zusammen. Erst in Üebung 2 benoetigt.
        '''
        self.read_connections_file()
        self.open_port()

    def receive_messages(self):
        '''
        * Empfaengt eine Nachricht auf dem Port auf dem der Prozess hoert.
        * Deserialisiert die Nachricht
        * loggt die Nachricht
        * verarbeitet die Nachricht in der abstrakten Methode process_received_message()
        '''
        connection, addr = self.__listeningSocket.accept()
        data = connection.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("empfangen: " + message.printToString())
            self.process_received_message(message)

    @abstractmethod
    def process_received_message(self, message):
        pass

    def send_message_to_id(self, message, ID):
        '''
        Sendet eine Nachricht an den Prozess mit der uebergebenen ID.
        * Oeffnet einen Socket
        * ermittelt die IP und den Port des Empfängers
        * serialisiert die Nachricht und sendet sie an den Empfaenger
        Das Ergebnis wird geloggt.
        '''
        try:
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver = self._ips_and_ports[str(ID)]
            sender.connect((receiver["ip"], receiver["port"]))
            sender.sendall(cPickle.dumps(message))
            self.logger.info("gesendet an: " + str(ID) + " Message: " + message.printToString())
        except:
            self.logger.error("Error while sending message to " + ID, exc_info=1)

    def choose_new_neighbours(self, amount_neighbours):
        '''
        Wähle per Zufall amount_neighbours -viele Nachbarn. Wird in der Uebung 1 einmal aufgerufen,
        in der Uebung 2 mehrmals. Die IDs der neuen Nachbarn werden geloggt.
        '''
        self._neighbours.clear()
        ips_and_ports_copy = self._ips_and_ports.copy()
        for i in range(amount_neighbours):
            random_index = self._system_random.randint(0, len(ips_and_ports_copy) - 1)
            ID = ips_and_ports_copy.keys()[random_index]
            self._neighbours[ID] = self._ips_and_ports[ID]
            del ips_and_ports_copy[ID]
        self.logger.info("Neue Nachbarn: " + str(self._neighbours))




