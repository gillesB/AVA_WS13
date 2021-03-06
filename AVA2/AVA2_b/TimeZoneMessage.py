from CodeBase.Message import Message

__author__ = 'me'


class TimeZoneMessage(Message):
    '''
    Eine Nachricht die ein Feld fuer eine Zeitzone enthaelt. Wird fuer das Zeitzonenverfahren benoetigt.
    '''
    def __init__(self, action, message="", control=False, sender=None, time_zone=0):
        Message.__init__(self, action, message, control, sender)
        self.time_zone = time_zone

    def printToString(self):
        return Message.printToString(self) + " Timezone: " + str(self.time_zone)

