from AVA1.AVA1_a.LocalKnot import LocalKnot

__author__ = 'me'


class GraphKnot(LocalKnot):
    '''
    Ein einfacher Knoten, der von LocalKnot erbt. Der Unterschied ist, dass er seine Nachbarn nicht per Zufall bestimmt,
    sondern diese aus einer Graphviz Datei bezieht.
    '''
    def __init__(self, ID, connections_filename, topology_filename):
        super(GraphKnot, self).__init__(ID, connections_filename)
        self.__topology_filename = topology_filename

    def choose_new_neighbours(self, n):
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
                    elif line[3] == self.getID():
                        ID = line[1]
                        self._neighbours[ID] = self._ips_and_ports[ID]
        self.logger.info("Neue Nachbarn: " + str(self._neighbours))