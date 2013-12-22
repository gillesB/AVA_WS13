__author__ = 'me'


class Message():
    '''
    Eine einfache Nachricht, die serialisiert werden kann, uebers Netzwerk versendet werden kann und
    danach wieder deserialisiert werden kann.
    '''

    def __init__(self, action, message="", control=False, sender=None):
        self.__control = control # i.d.R ein boolean der angibt, ob es sich um eine Kontrollnachricht handelt,
        #sprich ob die Nachricht von einem Beobachter stammt (True = Nachricht kommt von einem Beobachter).
        self.__message = message # die eigentlichen Daten die verwendet werden sollen
        self.__action = action # eine Aktion, auf die die Knoten reagieren koennen, z.B. um die empfangen Daten zu verarbeiten
        self.__sender = sender # der Absender der Nachricht

    def printToString(self):
        return_str = ""
        if self.__control:
            control = '(Kontrollnachricht) '
            return_str += control
        return_str = return_str + 'Aktion: ' + str(self.__action) + ' Inhalt: ' + str(self.__message)
        if self.__sender:
            return_str = return_str + ' Sender: ' + str(self.__sender)
        return return_str

    def getAction(self):
        return self.__action

    def getMessage(self):
        return self.__message

    def getSender(self):
        return self.__sender
