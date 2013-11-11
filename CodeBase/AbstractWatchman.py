from abc import abstractmethod
import cPickle
import logging
import socket
import json


__author__ = 'me'


class AbstractWatchman:

    def __init__(self, topology_filename):
        self._ips_and_ports = {}
        self.__topology_filename = topology_filename
        self.logger = logging.getLogger(__name__)
        self.read_input_file()

    def read_input_file(self):
        json_data = open(self.__topology_filename)
        self._ips_and_ports = json.load(json_data)
        json_data.close()

    def send_message_to_id(self, ID, message):
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