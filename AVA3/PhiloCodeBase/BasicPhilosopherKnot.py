import time
from CodeBase.AbstractGraphKnot import AbstractGraphKnot
from CodeBase.Message import Message

__author__ = 'me'


class BasicPhilosopherKnot(AbstractGraphKnot):
    TIME_THINK_MAX = 4000
    TIME_EAT_MAX = 4000

    def __init__(self, ID, connections_filename, topology_filename):
        super(BasicPhilosopherKnot, self).__init__(ID, connections_filename, topology_filename)
        self.has_left_fork = False
        self.has_right_fork = False
        self.waiting_for = None

    def think(self):
        time_to_think = self._system_random.randint(0, BasicPhilosopherKnot.TIME_THINK_MAX) / 1000.0  # [s = ms / 1000]
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        time.sleep(time_to_think)

    def eat(self):
        time_to_eat = self._system_random.randint(0, BasicPhilosopherKnot.TIME_EAT_MAX) / 1000.0 # [s = ms / 1000]
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        time.sleep(time_to_eat)

    def process_received_message(self, connection, message):
        if message.getAction() == "receiveFork":
            if message.getSender() == self.rightNeighbour:
                self.has_right_fork = True
            else:
                self.has_left_fork = True
            self.waiting_for = None

    def order_left_fork(self):
        self.order_fork(self.leftNeighbour)

    def order_right_fork(self):
        self.order_fork(self.rightNeighbour)

    def order_fork(self, ID):
        self.waiting_for = ID
        order_fork_message = Message("orderFork", "Are you free?", sender=self._ID)
        self.send_message_to_id(order_fork_message, ID)

    def return_left_fork(self):
        return_fork_message = Message("returnFork", "Left fork, you are free now.", sender=self._ID)
        if self.send_message_to_id(return_fork_message, self.leftNeighbour):
            self.has_left_fork = False

    def return_right_fork(self):
        return_fork_message = Message("returnFork", "Right fork, you are free now.", sender=self._ID)
        if self.send_message_to_id(return_fork_message, self.rightNeighbour):
            self.has_right_fork = False

    def return_forks(self):
        self.return_left_fork()
        self.return_right_fork()





