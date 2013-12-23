from CodeBase.AbstractKnot import AbstractKnot

__author__ = 'me'


class AbstractGraphKnot(AbstractKnot):
    '''
    Ein abstrakter Knoten, der von AbstractKnot erbt. Er kann seine Nachbar ueber eine Graphviz Datei ermitteln.
    '''

    def __init__(self, ID, connections_filename, topology_filename):
        super(AbstractGraphKnot, self).__init__(ID, connections_filename)
        self.__topology_filename = topology_filename
        self.rightNeighbour = None
        self.leftNeighbour = None

    def choose_new_neighbours(self, n=None):
        '''
        Parsen der Graphviz Datei und bestimmen der Nachbarn.
        * Zeilenweises Lesen der Datei
        * Zeile ignorieren, falls sie nicht mit " beginnt
        * Ansonsten Zeile bei jedem " splitten
        * Resultat ist ein Array mit folgendem Aufbau: ["", "ID1", " - ", "ID2", ""]
        * Falls ID1 oder ID2 der eigenen ID entspricht, dann ist die jeweils andere ID die ID eines Nachbarns
        '''
        with open(self.__topology_filename, 'rU') as f:
            for line in f:
                if line[0] == '"':
                    line = line.split('"')
                    if line[1] == self.getID():
                        ID = line[3]
                        self._neighbours[ID] = self._ips_and_ports[ID]
                        self.rightNeighbour = ID
                    elif line[3] == self.getID():
                        ID = line[1]
                        self._neighbours[ID] = self._ips_and_ports[ID]
                        self.leftNeighbour = ID
        self.logger.info("Neue Nachbarn: " + str(self._neighbours))