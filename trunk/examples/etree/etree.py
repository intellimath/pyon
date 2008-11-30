from pyon import loads, dumps

__all__ = ['Node', 'Leaf', 'resolverName']

def resolverName(name):
    """
    Return new function for creation
    of node or leaf with a given tag name
    or return existing one from the cache.
    """
    def func(value=None, tag=name):
        if value is None:
            e = Node(tag)
        else:
            e = Leaf(tag, value)
        return e
    func.__name__ = name
    func.__module__ = '__cache__'
    return func

class Leaf(object):
    def __init__(self, _tag, _value, **kw):
        self._tag = _tag
        self._value = _value
        self.__dict__.update(kw)
    #
    @property
    def tag(self):
        return self._tag
    #
    @property
    def value(self):
        return self._value
    #
    def __reduce__(self):
        _dict = dict(self.__dict__)
        _tag = _dict.pop('_tag')
        _value = _dict.pop('_value')
        return resolverName(_tag), (_value,), _dict
    #
    def __setstate__(self, state):
        self.__dict__.update(state)

class Node(object):
    #
    def __init__(self, _tag, **kw):
        self._tag = _tag
        self.__dict__.update(kw)
        self._children = []
    #
    @property
    def tag(self):
        return self._tag
    #
    @property
    def children(self):
      return self._children
    #
    def append(self, element):
        self._children.append(element)
    #
    def __reduce__(self):
        _dict = dict(self.__dict__)
        _tag = _dict.pop('_tag')
        _children = _dict.pop('_children')
        return resolverName(_tag), (), _dict, _children
    #
    def __setstate__(self, state):
        self.__dict__.update(state)

if __name__ == '__main__':
    res = loads("""
menu(id='File',
  *[ item(id='Open', action='OpenFile'),
     item(id='Close', action='CloseFile'),
     menu(id='SendTo',
       *[ item(id='Desktop', action='SendToDesktop'),
          item(id='RemoteDesktop', action='SendToRemoteDesktop')
        ]
     )
   ]
)
""", resolver=resolverName)

    print(dumps(res, pretty=True))

    res = loads("""
menu(id='File',
  *[ item(id='Open', action='OpenFile'),
     item(id='Close', action='CloseFile'),
     menu(id='SendTo',
       *[ item(id='Desktop', action='SendToDesktop'),
          item(id='RemoteDesktop', action='SendToRemoteDesktop')
        ]
     )
   ]
)
""", safe=True)

    print(dumps(res, pretty=True, fast=True))

