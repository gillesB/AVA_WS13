from AVA3.PhiloCodeBase.BasicForkKnot import BasicForkKnot

__author__ = 'me'


class EdgeChasingForkKnot(BasicForkKnot):
    '''
    Ein Gabel Knoten der das Edge Chasing Verfahren ermoeglicht.
    '''

    def __init__(self, ID, connections_filename, topology_filename):
        super(EdgeChasingForkKnot, self).__init__(ID, connections_filename, topology_filename)

    def process_received_message(self, connection, message):
        '''
        Bei erhalt der isDeadlock Nachricht:
        * Ueberpruefen ob die Nachricht bereits empfangen wurde, falls ja -> verwerfen
        * Ueberpruefen ob die Gabel angefordert wurde, falls nein -> verwerfen
        * Sonst: sich in die Nachricht vermekren und an den Besitzer der Gabel weiterleiten
        '''
        super(EdgeChasingForkKnot, self).process_received_message(connection, message)
        if message.getAction() == "isDeadlock":
            if self._ID not in message.getMessage():
                if self.ordered_by:
                    self.logger.info("Sending isDeadlock message to my owner, to ask if he is waiting for another fork.")
                    message.getMessage().append(self._ID)
                    self.send_message_to_id(message, self.owner)
                else:
                    self.logger.info("Having no owner. No deadlock was found.")
            else:
                self.logger.info("I already appear in the message. No deadlock was found.")



