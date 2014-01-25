import socket
import time
from datetime import datetime
import cPickle
from AVA3.PhiloCodeBase.BasicPhilosopherKnot import BasicPhilosopherKnot
from CodeBase.Message import Message

__author__ = 'me'


class EdgeChasingPhiloKnot(BasicPhilosopherKnot):
    def __init__(self, ID, connections_filename, topology_filename):
        super(EdgeChasingPhiloKnot, self).__init__(ID, connections_filename, topology_filename)
        self.requested_fork_at_possible_deadlock = None

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.wait_till_full_second()
            self.think()
            self.logger.info("I want to eat now.")
            self.order_and_receive_forks()
            self.eat()
            self.return_forks()


    def open_port(self):
        super(EdgeChasingPhiloKnot, self).open_port()
        # set timeout
        seconds = 3 + self._system_random.random()
        self._listeningSocket.settimeout(seconds)

    #Uberschreibungen den Methoden die wahrscheinlich Deadlock ausloesen
    def think(self):
        time_to_think = 2  # [s = ms / 1000]
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        time.sleep(time_to_think)

    def eat(self):
        time_to_eat = 2  # [s = ms / 1000]
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        time.sleep(time_to_eat)

    @staticmethod
    def wait_till_full_second():
        '''
        Warte bis zur naechten vollen Sekunde, so dass Deadlock wahrscheinlicher wird
        '''
        now = datetime.now()
        time.sleep(1 - now.microsecond / 1000000.0)

    def process_received_message(self, connection, message):
        super(EdgeChasingPhiloKnot, self).process_received_message(connection, message)
        if message.getAction() == "isDeadlock":
            '''
            Ueberpruefen ob es sich um einen Deadlock handeln koennte.
            Es handelt sich wahrscheinlich um einen Deadlock falls:
            * auf eine Gabel gewartet wird
            * die Nachricht nicht von dem Nachbar kommt an den sie urspruenglich geschickt wurde
            * und man selbst die Nachricht gesendet hat oder man die Nachricht nicht bereits empfangen hatte
            '''
            if self.waiting_for and message.getMessage()[-1] != self.requested_fork_at_possible_deadlock and (
                    message.getMessage()[0] == self._ID or self._ID not in message.getMessage()):
            #possible deadlock
                if message.getMessage()[0] == self._ID:
                    #is deadlock
                    self.logger.info("A deadlock was found.")
                    self.resolve_deadlock()
                else:
                    #might be a deadlock
                    # Nachricht an die Gabel senden, auf die man wartet
                    self.logger.info("Sending isDeadlock message to requested fork.")
                    message.getMessage().append(self._ID)
                    self.send_message_to_id(message, self.waiting_for)
            else:
                #no deadlock
                #Logging Ausgabe
                if not self.waiting_for:
                    self.logger.info("Not waiting for a fork. No deadlock was found.")
                elif message.getMessage()[-1] == self.requested_fork_at_possible_deadlock:
                    self.logger.info("Received the isDeadlock message from requested fork. No deadlock was found.")
                elif self._ID in message.getMessage():
                    self.logger.info("I already am in the list of the isDeadlock message. No deadlock was found.")
                else:
                    self.logger.info("Strange another case appeared. No deadlock was found.")
        elif message.getAction() == "checkDeadlock":
            self.check_deadlock()

    def check_deadlock(self):
        is_deadlock_message = Message("isDeadlock", list(self._ID), True, self._ID)
        if not self.waiting_for:
            self.logger.info("Having both forks. No deadlock.")
        else:
            self.logger.info("Sending isDeadlock message to requested fork.")
            self.requested_fork_at_possible_deadlock = self.waiting_for
            self.send_message_to_id(is_deadlock_message, self.waiting_for)

    def resolve_deadlock(self):
        '''
        Deadlock aufloesen. Falls man linke Gabel hat, dann wird diese zurueckgegeben. Falls man die rechte Gabel hat,
        dann wird diese zurueckgegeben.
        '''
        if self.has_left_fork:
            self.logger.info("To resolve the deadlock, I return my left fork.")
            self.return_left_fork()
        if self.has_right_fork:
            self.logger.info("To resolve the deadlock, I return my right fork.")
            self.return_right_fork()

    def order_and_receive_forks(self):
        '''
        Versuch beide Gabeln zu erhalten.
        Solange man nicht beide Gabeln hat.
        * Versuch die linke Gabel zu erhalten
        * Versuch die rechte Gabel zu erhalten
        Bei einem Versuch wird:
        * diese angefordert
        * der Prozess blockiert
        * Erhalt der Gabel
        Dies muss in der while Schleife stattfinden, da durch Deadlockaufloesung kann,
        vor erhalt der rechten Gabel die linke wieder weg sein.
        Oder umgedreht.
        '''
        while not (self.has_right_fork and self.has_left_fork):
            if not self.has_right_fork:
                self.logger.info("Waiting for the right fork.")
                self.order_right_fork()
                while not self.has_right_fork:
                    self.receive_messages()
                self.logger.info("I received the right fork.")
            if not self.has_left_fork:
                self.logger.info("Waiting for the left fork.")
                self.order_left_fork()
                while not self.has_left_fork:
                    self.receive_messages()
                self.logger.info("I received the left fork.")
        if self.has_right_fork and self.has_left_fork:
            self.logger.info("I received the two forks.")
        else:
            self.logger.error("This should never happen.")

    def receive_messages(self):
        '''
        * Empfaengt eine Nachricht auf dem Port auf dem der Prozess hoert.
        * Deserialisiert die Nachricht
        * loggt die Nachricht
        * verarbeitet die Nachricht in der abstrakten Methode process_received_message()
        * wartet allerdings nur bis zum Timeout, danach wird ueberprueft ob ein Deadlock vorliegt
        '''
        try:
            connection, addr = self._listeningSocket.accept()
            data = connection.recv(1024)
            if data:
                message = cPickle.loads(data)
                self.logger.info("empfangen: " + message.printToString())
                self.process_received_message(connection, message)
        except socket.timeout:
            self.logger.info("Got a timeout while waiting for a new message. Checking if it could be a deadlock.")
            self.check_deadlock()





