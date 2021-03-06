from AVA2.AVA2_b.TimeZoneMessage import TimeZoneMessage

__author__ = 'me'


class StatisticsMessage(TimeZoneMessage):
    '''
    Eine Zeitzonennachricht die zwei Felder fuer die Anzahl der gesendeten und die Anzahl der empfangenen Nachrichten
    enthaelt.
    '''

    def __init__(self, sender, messages_sent, messages_received, time_zone):
        TimeZoneMessage.__init__(self, action="statistics", message=None, control=True, sender=sender,
                                 time_zone=time_zone)
        self.messages_sent = messages_sent
        self.messages_received = messages_received

