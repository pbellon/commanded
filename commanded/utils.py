# Python Object
class PO(object):
    def __init__(self, dc = {}):
        super(PO, self).__init__()
        for key, val in dc.items():
            setattr(self, key, val)

def as_obj(dc):
    """
    Returns a dict as a python object
    """
    return PO(dc)

def add_method(obj, method, name=None):
    """
    Adds a method to an object with an optional name, will use passed function
    name otherwise
    """
    if name is None:
        name = method.__name__
    setattr(obj, name, method)
