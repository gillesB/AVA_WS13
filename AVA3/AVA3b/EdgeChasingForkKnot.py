from AVA3.PhiloCodeBase.BasicForkKnot import BasicForkKnot

__author__ = 'me'


class EdgeChasingForkKnot(BasicForkKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(EdgeChasingForkKnot, self).__init__(ID, connections_filename, topology_filename)

    def process_received_message(self, connection, message):
        super(EdgeChasingForkKnot, self).process_received_message(connection, message)
        if message.getAction() == "isDeadlock":
            # leite Nachricht weiter
            neighbour_id = self.rightNeighbour
            self.send_message_to_id(message, neighbour_id)



