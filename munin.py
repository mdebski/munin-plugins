"""Trivial module simplifying munin plugins creation"""

class MultiGraphs(object):
    """Multiple graphs from one plugin"""

    def __init__(self, graphs=None):
        if graphs is not None:
            self.graphs = graphs
        else:
            self.graphs = []

    def append(self, graph):
        self.graphs.append(graph)

    def set_value(self, item, value, graph=None):
        for g in self.graphs:
            if graph is None or g.name == graph:
                g.set_value(item, value)

    def update_values(self):
        """Used if items generate values on their own"""
        for g in self.graphs:
            g.update_values()

    def str_config(self):
        return '\n'.join(['multigraph %s\n%s' % (g.name, g.str_config())
                          for g in self.graphs])

    def str_value(self):
        return '\n'.join(['multigraph %s\n%s' % (g.name, g.str_value())
                          for g in self.graphs])

    def print_config(self):
        print(self.str_config())        

    def print_value(self):
        print(self.str_value())        


class Graph(object):
    """Single graph, possibly with multiple items (data sources)"""

    params = ['title', 'category', 'args', 'vlabel', 'info']

    def __init__(self, name, title=None, category=None, args=None, vlabel=None,
                 info=None):
        self.name = name
        self.items = []
        if title is not None:
            self.title = title 
        else:
            self.title = name
        self.category = category
        self.args = args
        self.vlabel = vlabel
        self.info = info

    def append(self, item):
        self.items.append(item)

    def set_value(self, item, value):
        for i in self.items:
            if i.name == item:
                i.set_value(value)

    def update_values(self):
        """Used if items generate values on their own"""
        for i in self.items:
            i.update_value()

    def str_value(self):
        return '\n'.join([i.str_value() for i in self.items])

    def str_config(self):
        s = '\n'.join(["graph_%s %s" % (attr, getattr(self, attr))
                       for attr in self.params
                       if getattr(self, attr, None) is not None])
        s += "\ngraph_order %s\n" % ' '.join([i.name for i in self.items])
        for i in self.items:
            s += i.str_config() + '\n'
        return s

    def print_config(self):
        print(self.str_config())        

    def print_value(self):
        print(self.str_value())        

def bool2yn(b):
    if b:
        return 'yes'
    else:
        return 'no'

class Item(object):
    """Single data source"""

    params = ['label', 'type', 'cdef', 'min', 'max', 'draw']

    def __init__(self, name, label='', type=None, graph=True, cdef=None,
                 min=None, max=None, draw=None):
        self.name = name
        self.value = None

        self.label = label
        self.type = type
        self.graph = graph
        self.cdef = cdef
        self.min = min
        self.max = max
        self.draw = draw

    def set_value(self, value):
        self.value = value

    def update_value(self):
        """Override if item shall be responsible for getting value"""
        raise NotImplementedError()

    def str_value(self):
        return '%s.value %s' % (self.name, self.value)

    def str_config(self):
        s = '\n'.join(["%s.%s %s" % (self.name, attr, getattr(self, attr))
                       for attr in self.params
                       if getattr(self, attr, None) is not None])
        s += '\n%s.graph %s' % (self.name, bool2yn(self.graph)) 
        return s
