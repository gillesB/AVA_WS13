from sets import Set
import socket
import time
import cPickle
import datetime
from AVA3.PhiloCodeBase.BasicPhilosopherKnot import BasicPhilosopherKnot
from CodeBase.Message import Message

__author__ = 'me'

class MisraPhiloKnot(BasicPhilosopherKnot):

    def __init__(self, ID, connections_filename, topology_filename, force_forks=1):
        super(MisraPhiloKnot, self).__init__(ID, connections_filename, topology_filename)
        self.right_fork_clean = False
        self.left_fork_clean = False
        self.clean_requests = Set()
        self.force_forks = force_forks

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        #Warte eine Sekunde, bis Gabeln bereit sind
        time.sleep(1)
        #fordere Anfangsgabeln an
        if self.force_forks == 1:
            self.force_right_fork()
        elif self.force_forks == 2:
            self.force_right_fork()
            self.force_left_fork()
        while True:
            self.think()
            self.treat_clean_requests()
            self.logger.info("I want to eat now.")
            self.order_and_receive_forks()
            self.eat()
            self.make_forks_dirty()
            self.treat_clean_requests()
            #self.return_forks()

    def process_received_message(self, connection, message):
        super(MisraPhiloKnot, self).process_received_message(connection, message)
        if message.getAction() == "cleanMe":
            self.clean_requests.add(message.getSender())

    def treat_clean_requests(self):
        make_clean_message = Message("setClean", True, sender=self._ID)
        if self.leftNeighbour in self.clean_requests:
            if self.has_left_fork and not self.left_fork_clean:
                if self.send_message_to_id(make_clean_message, self.leftNeighbour):
                    self.left_fork_clean = True
                    self.logger.info("The left fork is clean.")
                    self.return_left_fork()
                    self.clean_requests.remove(self.leftNeighbour)
        if self.rightNeighbour in self.clean_requests:
            if self.has_right_fork and not self.right_fork_clean:
                if self.send_message_to_id(make_clean_message, self.rightNeighbour):
                    self.right_fork_clean = True
                    self.logger.info("The right fork is clean.")
                    self.return_right_fork()
                    self.clean_requests.remove(self.rightNeighbour)

    def order_and_receive_forks(self):
        while not (self.has_right_fork and self.has_left_fork):
            if not self.has_right_fork:
                self.logger.info("Waiting for the right fork.")
                self.order_right_fork()
                while not self.has_right_fork:
                    self.receive_messages()
                self.logger.info("I received the right fork.")
                self.right_fork_clean = True
            if not self.has_left_fork:
                self.logger.info("Waiting for the left fork.")
                self.order_left_fork()
                while not self.has_left_fork:
                    self.receive_messages()
                self.logger.info("I received the left fork.")
                self.left_fork_clean = True
        if self.has_right_fork and self.has_left_fork:
            self.logger.info("I received the two forks.")
        else:
            self.logger.error("This should never happen.")

    def make_forks_dirty(self):
        make_dirty_message = Message("setClean", False, sender=self._ID)
        if self.send_message_to_id(make_dirty_message, self.leftNeighbour):
            self.left_fork_clean = False
            self.logger.info("The left fork is dirty.")
        if self.send_message_to_id(make_dirty_message, self.rightNeighbour):
            self.right_fork_clean = False
            self.logger.info("The right fork is dirty.")

    def force_right_fork(self):
        force_fork_message = Message("forceFork", sender=self._ID)
        if self.send_message_to_id(force_fork_message, self.rightNeighbour):
            self.has_right_fork = True
            self.right_fork_clean = False

    def force_left_fork(self):
        force_fork_message = Message("forceFork", sender=self._ID)
        if self.send_message_to_id(force_fork_message, self.leftNeighbour):
            self.has_left_fork = True
            self.left_fork_clean = False

    def wait_and_listen(self, seconds):
        now = datetime.datetime.now()
        wait_till = now + datetime.timedelta(0, seconds)
        while seconds > 0.0001:
            self.logger.info("Still waiting for " + str(seconds))
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

    def think(self):
        #time_to_think = self._system_random.randint(0, BasicPhilosopherKnot.TIME_THINK_MAX) / 1000.0  # [s = ms / 1000]
        time_to_think = 2
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        self.wait_and_listen(time_to_think)

    def eat(self):
        #time_to_eat = self._system_random.randint(0, BasicPhilosopherKnot.TIME_EAT_MAX) / 1000.0 # [s = ms / 1000]
        time_to_eat = 2
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        self.wait_and_listen(time_to_eat)



