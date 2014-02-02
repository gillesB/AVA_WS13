import socket
import datetime
import cPickle
import time
from CodeBase.AbstractGraphKnot import AbstractGraphKnot
from CodeBase.Message import Message

__author__ = 'me'


class BasicPhilosopherKnot(AbstractGraphKnot):
    '''
    Eine einfacherer Philosphenknoten aus dem Philosphenproblem
    '''
    TIME_THINK_MAX = 500
    TIME_EAT_MAX = 1000
    MINUTES_TO_RUN = 1

    def __init__(self, ID, connections_filename, topology_filename):
        super(BasicPhilosopherKnot, self).__init__(ID, connections_filename, topology_filename)
        self.has_left_fork = False # besitzt linke Gabel
        self.has_right_fork = False # besitzt rechte Gabel
        self.waiting_for = None # wartet auf Gabel mit der ID, er kann immer nur auf eine Gabel warten
        self.total_time_eat = 0
        self.amount_eaten = 0
        self.amount_sent_messages = 0
        self.amount_received_messages = 0
        self.time_to_end = datetime.datetime.now() + datetime.timedelta(minutes=self.MINUTES_TO_RUN)
        self.start_clock = time.clock()
        self.total_time_waiting_for_forks = 0
        self.time_waiting_for_fork_start = 0

    def think(self):
        '''
        Der Philosoph denkt fuer eine bestimmte Zeit. Er ist waehrendem blockiert.
        '''
        #time_to_think = self._system_random.randint(0, BasicPhilosopherKnot.TIME_THINK_MAX) / 1000.0  # [s = ms / 1000]
        time_to_think = BasicPhilosopherKnot.TIME_THINK_MAX / 1000.0
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        self.wait_and_listen(time_to_think)

    def eat(self):
        '''
        Der Philosoph isst fuer eine bestimmte Zeit. Er ist waehrendem blockiert.
        '''
        #time_to_eat = self._system_random.randint(0, BasicPhilosopherKnot.TIME_EAT_MAX) / 1000.0 # [s = ms / 1000]
        time_to_eat = BasicPhilosopherKnot.TIME_EAT_MAX / 1000.0
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        self.wait_and_listen(time_to_eat)
        self.total_time_eat += time_to_eat
        self.amount_eaten += 1

    def process_received_message(self, connection, message):
        if message.getAction() == "receiveFork":
            # er erhaelt eine Gabel
            if message.getSender() == self.rightNeighbour:
                self.has_right_fork = True
            else:
                self.has_left_fork = True
            self.waiting_for = None
            waiting_time = time.time() - self.time_waiting_for_fork_start
            self.logger.info("Waited for fork [s]: " + str(waiting_time))
            self.total_time_waiting_for_forks += waiting_time

    def order_left_fork(self):
        self.order_fork(self.leftNeighbour)

    def order_right_fork(self):
        self.order_fork(self.rightNeighbour)

    def order_fork(self, ID):
        '''
        fordere Gabel an
        '''
        self.waiting_for = ID
        order_fork_message = Message("orderFork", "Are you free?", sender=self._ID)
        self.send_message_to_id(order_fork_message, ID)
        self.time_waiting_for_fork_start = time.time()

    def return_left_fork(self):
        '''
        Gib die linke Gabel zurueck
        '''
        return_fork_message = Message("returnFork", "Left fork, you are free now.", sender=self._ID)
        if self.send_message_to_id(return_fork_message, self.leftNeighbour):
            self.has_left_fork = False

    def return_right_fork(self):
        '''
        Gib die rechte Gabel zurueck
        '''
        return_fork_message = Message("returnFork", "Right fork, you are free now.", sender=self._ID)
        if self.send_message_to_id(return_fork_message, self.rightNeighbour):
            self.has_right_fork = False

    def return_forks(self):
        '''
        Gib beide Gabeln zurueck
        '''
        if self.has_left_fork:
            self.return_left_fork()
        if self.has_right_fork:
            self.return_right_fork()

    def wait_and_listen(self, seconds):
        '''
        Wartet eine gewisse Zeit und lauscht waehrendem auf dem offenen Port.
        '''
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

    def receive_messages(self):
        super(BasicPhilosopherKnot, self).receive_messages()
        self.amount_received_messages += 1

    def send_message_over_socket(self, socket1, message):
        self.amount_sent_messages += 1
        return super(BasicPhilosopherKnot, self).send_message_over_socket(socket1, message)

    def send_message_to_id(self, message, ID):
        self.amount_sent_messages += 1
        return super(BasicPhilosopherKnot, self).send_message_to_id(message, ID)


    def print_final_information(self):
        self.logger.info("Totale Essenszeit: " + str(self.total_time_eat))
        self.logger.info("Anzahl Essen: " + str(self.amount_eaten))
        self.logger.info("Anzahl gesendeter Nachrichten: " + str(self.amount_sent_messages))
        self.logger.info("Anzahl empfangener Nachrichten: " + str(self.amount_received_messages))
        self.logger.info("verbrauchte Rechenzeit: " + str(time.clock() - self.start_clock))
        self.logger.info("auf Gabel gewartet: " + str(self.total_time_waiting_for_forks))

    def have_i_still_time_to_run(self):
        if datetime.datetime.now() < self.time_to_end:
            return True
        else:
            return False










