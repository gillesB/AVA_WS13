from AVA1.AVA1_a.LocalKnot import LocalKnot

__author__ = 'me'

class LocalKnotGraphviz(LocalKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(LocalKnotGraphviz, self).__init__(ID, connections_filename)
        self.__topology_filename = topology_filename

    def choose_neighbours(self):
        with open(self.__topology_filename, 'rU') as f:
            for line in f:
                if line[0] == '"':
                    line = line.split('"')
                    if line[1] == self.getID():
                        self.add_neighbour(line[3])
                    elif line[3] == self.getID():
                        self.add_neighbour(line[1])