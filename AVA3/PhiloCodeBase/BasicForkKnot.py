from CodeBase.Message import Message
from CodeBase.AbstractGraphKnot import AbstractGraphKnot

__author__ = 'me'


class BasicForkKnot(AbstractGraphKnot):
    '''
    Ein einfacherer Gabel Knoten aus dem Philosophenproblem.
    '''

    def __init__(self, ID, connections_filename, topology_filename):
        super(BasicForkKnot, self).__init__(ID, connections_filename, topology_filename)
        self.free = True # gibt an op die Gabel einen Besitzer hat
        self.owner = None # Besitzer der Gabel
        self.ordered_by = -1 # gibt an ob die Gabel von jemandem angefragt wurde. -1 = Niemand

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.give_philosopher_a_fork()
            self.receive_messages()

    def process_received_message(self, connection, message):
        if message.getAction() == "orderFork":
            self.ordered_by = message.getSender()
            self.logger.info("I was ordered by " + message.getSender())
        elif message.getAction() == "returnFork":
            self.set_free(message.getSender())

    def give_philosopher_a_fork(self):
        '''
        Gib die Gabel dem Philosophen der sie angefordert hat.
        '''
        if self.free and self.ordered_by >= 0:
            philosopher_receives_fork_message = Message("receiveFork", "A fork for a philiospher.", sender=self._ID)
            self.send_message_to_id(philosopher_receives_fork_message, self.ordered_by)
            self.owner = self.ordered_by
            self.free = False
            self.ordered_by = -1
            self.logger.info("My new owner is " + self.owner)

    def set_free(self, request_comes_from_id):
        '''
        Die Gabel wird nicht mehr von ihrem vorherigen Besitzer benutzt.
        '''
        if request_comes_from_id == self.owner:
            self.free = True
            self.owner = None
            self.logger.info("I have no owner.")


