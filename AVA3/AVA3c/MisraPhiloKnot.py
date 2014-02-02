import time
from AVA3.PhiloCodeBase.BasicPhilosopherKnot import BasicPhilosopherKnot
from CodeBase.Message import Message

__author__ = 'me'


class MisraPhiloKnot(BasicPhilosopherKnot):
    '''
    Ein Philosophenknoten nach Chandy / Misra
    '''
    def __init__(self, ID, connections_filename, topology_filename, force_forks=1):
        super(MisraPhiloKnot, self).__init__(ID, connections_filename, topology_filename)
        self.right_fork_clean = False
        self.left_fork_clean = False
        self.clean_requests = set()
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
        while self.have_i_still_time_to_run():
            self.think()
            self.treat_clean_requests()
            self.logger.info("I want to eat now.")
            self.order_and_receive_forks()
            self.eat()
            self.make_forks_dirty()
            self.treat_clean_requests()
        make_clean_message = Message("setClean", True, sender=self._ID)
        if self.has_right_fork:
            self.send_message_to_id(make_clean_message, self.rightNeighbour)
        if self.has_left_fork:
            self.send_message_to_id(make_clean_message, self.leftNeighbour)
        self.return_forks()
        self.print_final_information()

    def process_received_message(self, connection, message):
        super(MisraPhiloKnot, self).process_received_message(connection, message)
        if message.getAction() == "cleanMe":
            self.clean_requests.add(message.getSender())

    def treat_clean_requests(self):
        '''
        Bearbeite die Anfragen der Gabel die geputzt werden wollen. Eine Gabel darf nur geputzt
        werden wenn diese auch schmutzig ist. Mit einer sauberen Gabel muss zuerst gegessen werde.
        Putze die Gabel und gib sie dann zurueck.
        '''
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
        '''
        Ordere und erhalte Gabeln.
        '''
        while not (self.has_right_fork and self.has_left_fork):
            self.logger.info("Check for the right fork.")
            if not self.has_right_fork:
                self.logger.info("Waiting for the right fork.")
                self.order_right_fork()
                while not self.has_right_fork:
                    self.receive_messages()
                self.logger.info("I received the right fork.")
                self.right_fork_clean = True
            else:
                self.logger.info("Already got the right fork.")

            self.logger.info("Check for the left fork.")
            if not self.has_left_fork:
                self.logger.info("Waiting for the left fork.")
                self.order_left_fork()
                while not self.has_left_fork:
                    self.receive_messages()
                self.logger.info("I received the left fork.")
                self.left_fork_clean = True
            else:
                self.logger.info("Already got the left fork.")

        if self.has_right_fork and self.has_left_fork:
            self.logger.info("I received the two forks.")
        else:
            self.logger.error("This should never happen.")

    def make_forks_dirty(self):
        '''
        Setzte die Gabeln auf schmutzig.
        '''
        make_dirty_message = Message("setClean", False, sender=self._ID)
        if self.send_message_to_id(make_dirty_message, self.leftNeighbour):
            self.left_fork_clean = False
            self.logger.info("The left fork is dirty.")
        if self.send_message_to_id(make_dirty_message, self.rightNeighbour):
            self.right_fork_clean = False
            self.logger.info("The right fork is dirty.")

    def force_right_fork(self):
        '''
        Erzwinge den Erhalt der rechten Gaabel. (Am Anfang)
        '''
        force_fork_message = Message("forceFork", sender=self._ID)
        if self.send_message_to_id(force_fork_message, self.rightNeighbour):
            self.has_right_fork = True
            self.right_fork_clean = False

    def force_left_fork(self):
        '''
        Erzwinge den Erhalt der linken Gaabel. (Am Anfang)
        '''
        force_fork_message = Message("forceFork", sender=self._ID)
        if self.send_message_to_id(force_fork_message, self.leftNeighbour):
            self.has_left_fork = True
            self.left_fork_clean = False




