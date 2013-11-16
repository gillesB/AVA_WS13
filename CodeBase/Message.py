__author__ = 'me'


class Message():
    '''
    Eine einfache Nachricht, die serialisiert werden kann, uebers Netzwerk versendet werden kann und
    danach wieder deserialisiert werden kann.
    '''

    def __init__(self, action, message="", control=False):
        self.__control = control # i.d.R ein boolean der angibt, ob es sich um eine Kontrollnachricht handelt,
        #sprich ob die Nachricht von einem Beobachter stammt (True = Nachricht kommt von einem Beobachter).
        self.__message = message # die eigentlichen Daten die verwendet werden sollen
        self.__action = action # eine Aktion, auf die die Knoten reagieren koennen, z.B. um die empfangen Daten zu verarbeiten

    def printToString(self):
        control = ""
        if self.__control:
            control = '(Kontrollnachricht)'
        return control + ' Aktion: ' + str(self.__action) + ' Nachricht: ' + str(self.__message)

    def getAction(self):
        return self.__action

    def getMessage(self):
        return self.__message
