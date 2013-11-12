from AVA1.AVA1_a.LocalKnot import LocalKnot

__author__ = 'me'


class GraphKnot(LocalKnot):
    def __init__(self, ID, connections_filename, topology_filename):
        super(GraphKnot, self).__init__(ID, connections_filename)
        self.__topology_filename = topology_filename

    def choose_new_neighbours(self, n):
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