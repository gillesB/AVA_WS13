import time
import cPickle
from CodeBase.AbstractGraphKnot import AbstractGraphKnot
from CodeBase.Message import Message

__author__ = 'me'


class TokenPhilosopherKnot(AbstractGraphKnot):
    TIME_THINK_MAX = 4000
    TIME_EAT_MAX = 4000

    def __init__(self, ID, connections_filename, topology_filename):
        super(TokenPhilosopherKnot, self).__init__(ID, connections_filename, topology_filename)
        self.token = False

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.think()
            self.logger.info("I want to eat now. Waiting for the token.")
            while not self.token:
                self.receive_messages()
            self.logger.info("Received the token. Waiting for the left fork.")
            while not self.getLeftFork():
                self.logger.info("I received the left fork.")
                time.sleep(0.05)
            self.logger.info("Waiting for the right fork.")
            while not self.getRightFork():
                self.logger.info("I received the right fork.")
                time.sleep(0.05)
            self.eat()
            self.freeForks()
            self.send_token_to_next_philosopher()

    def think(self):
        time_to_think = self._system_random.randint(0, TokenPhilosopherKnot.TIME_THINK_MAX) / 1000.0  # [s = ms / 1000]
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        time.sleep(time_to_think)

    def eat(self):
        time_to_eat = self._system_random.randint(0, TokenPhilosopherKnot.TIME_EAT_MAX) / 1000.0 # [s = ms / 1000]
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        time.sleep(time_to_eat)

    def process_received_message(self, connection, message):
        if message.getAction() == "token":
            self.token = True

    def send_token_to_next_philosopher(self):
        tokenMessage = Message("token", "Ready to eat?", sender=self._ID)
        neighbourID = self.rightNeighbour
        self.send_message_to_id(tokenMessage, neighbourID)
        self.token = False

    def getLeftFork(self):
        return self.getFork(self.leftNeighbour)

    def getRightFork(self):
        return self.getFork(self.rightNeighbour)

    def getFork(self, ID):
        forkMessage = Message("getFork", "Are you free?", sender=self._ID)
        socket = self.send_message_to_id(forkMessage, ID)
        data = socket.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("empfangen: " + message.printToString())
            return message.getMessage()
        return False

    def freeForks(self):
        setForkFreeMessage = Message("setFree", "You are free now.", sender=self._ID)
        self.send_message_to_id(setForkFreeMessage, self.leftNeighbour)
        self.send_message_to_id(setForkFreeMessage, self.rightNeighbour)




