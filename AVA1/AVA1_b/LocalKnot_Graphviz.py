from AVA1.AVA1_a.LocalKnot import LocalKnot

__author__ = 'me'

class LocalKnot_Graphviz(LocalKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(LocalKnot_Graphviz, self).__init__(ID, connections_filename)
        self.__topology_filename = topology_filename

    def read_file(self):
        for line in lines_in_file:
            if(not line.begins('"'))
                line = line.split('"')
                if(line[1]):

    def choose_neighbours(self):
        super(LocalKnot_Graphviz, self).choose_neighbours()