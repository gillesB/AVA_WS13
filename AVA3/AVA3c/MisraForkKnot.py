from AVA3.PhiloCodeBase.BasicForkKnot import BasicForkKnot
from CodeBase.Message import Message

__author__ = 'me'


class MisraForkKnot(BasicForkKnot):
    '''
    Ein Gabel Knoten nach Chandy / Misra. D.h. die Gabel kann geputzt oder schmutzig sein.
    '''

    def __init__(self, ID, connections_filename, topology_filename):
        super(MisraForkKnot, self).__init__(ID, connections_filename, topology_filename)
        self.clean = False

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        self.receive_messages()
        while True:
            self.give_philosopher_a_fork()
            self.receive_messages()

    def process_received_message(self, connection, message):
        if message.getAction() == "orderFork":
            self.ordered_by = message.getSender()
            self.logger.info("I was ordered by " + message.getSender())
            #if not self.clean:
            self.send_clean_request_to_owner()
        elif message.getAction() == "returnFork":
            self.set_free(message.getSender())
        elif message.getAction() == "setClean":
            if message.getMessage():
                self.logger.info("I am clean now.")
            else:
                self.logger.info("I am dirty now.")
            self.clean = message.getMessage()
        elif message.getAction() == "forceFork":
            # wird fuer die initialisierung benötigt.
            self.owner = message.getSender()
            self.free = False

    def send_clean_request_to_owner(self):
        '''
        Anfrage an den Besitzer dass er die Gabel putzt
        '''
        clean_me_message = Message("cleanMe", sender=self._ID)
        self.send_message_to_id(clean_me_message, self.owner)

    def give_philosopher_a_fork(self):
        '''
        Ein Philosoph kann die Gabel nur erhalten wenn diese sauber ist.
        '''
        if self.free and self.clean and self.ordered_by >= 0:
            philosopher_receives_fork_message = Message("receiveFork", "A fork for a philiospher.", sender=self._ID)
            self.send_message_to_id(philosopher_receives_fork_message, self.ordered_by)
            self.owner = self.ordered_by
            self.free = False
            self.ordered_by = -1
            self.logger.info("My new owner is " + self.owner)





