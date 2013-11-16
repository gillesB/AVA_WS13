from abc import abstractmethod
import cPickle
import logging
import socket
import json


__author__ = 'me'


class AbstractWatchman:
    '''
    Ein abstrakter Beobachter. Uebernimmt die einfachsten Aufgaben zum Kontrollieren der Knoten. Ist selbst kein Knoten.
    '''
    def __init__(self, topology_filename):
        self._ips_and_ports = {}
        self.__topology_filename = topology_filename
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        self.read_input_file()

    def read_input_file(self):
        '''
        Liest die Datei mit den Informationen über die Knoten die es im Netzwerk gibt und speichert
        sie in ein dictionary.
        Somit sind die IP und der Port aller Knoten mittels ihrerer ID abrufbar.
        '''
        json_data = open(self.__topology_filename)
        self._ips_and_ports = json.load(json_data)
        json_data.close()

    def send_message_to_id(self, ID, message):
        '''
        Sendet eine Nachricht an den Prozess mit der uebergebenen ID. Oeffnet dabei einen Socket,
        ermittelt die IP und den Port des Empfängers, serialisiert die Nachricht und sendet sie an den Empfaenger.
        Das Ergebnis wird geloggt.
        '''
        try:
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver = self._ips_and_ports[str(ID)]
            sender.connect((receiver["ip"], receiver["port"]))
            sender.sendall(cPickle.dumps(message))
            self.logger.info(message.printToString())
        except:
            self.logger.error('Error while sending message.', exc_info=1)

    @abstractmethod
    def user_interface(self):
        pass