import time
from datetime import datetime
from AVA3.PhiloCodeBase.BasicPhilosopherKnot import BasicPhilosopherKnot

__author__ = 'me'


class EdgeChasingPhiloKnot(BasicPhilosopherKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(EdgeChasingPhiloKnot, self).__init__(ID, connections_filename, topology_filename)

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.wait_till_full_second()
            self.think()
            self.logger.info("I want to eat now.")
            self.logger.info("Waiting for the right fork.")
            self.order_right_fork()
            while not self.has_right_fork:
                self.receive_messages()
            self.logger.info("I received the right fork.")
            self.logger.info("Waiting for the left fork.")
            self.order_left_fork()
            while not self.has_left_fork:
                self.receive_messages()
            self.logger.info("I received the left fork.")
            self.eat()
            self.return_forks()

    def think(self):
        time_to_think = 2  # [s = ms / 1000]
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        time.sleep(time_to_think)

    def eat(self):
        time_to_eat = 2  # [s = ms / 1000]
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        time.sleep(time_to_eat)

    def wait_till_full_second(self):
        now = datetime.now()
        time.sleep(1 - now.microsecond/1000000.0)