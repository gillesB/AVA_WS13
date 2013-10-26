import time

__author__ = 'me'


class Message():
    def __init__(self, action, message="", control=False):
        self.__control = control
        self.__message = message
        self.__action = action

    def printToString(self):
        control = ""
        if self.__control:
            control = '(Kontrollnachricht)'
        return control + ' Aktion: ' + str(self.__action) + ' Nachricht: ' + str(self.__message)

    def getAction(self):
        return self.__action
