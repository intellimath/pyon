from pyon import loads, dumps

__all__ = ['Element', 'Item', 'resolverName']

cache = {}
def resolverName(name):
    func = cache.get(name, None)
    if func is None:
        def func(value=None, tag=name):
            if value is None:
                e = Element(tag)
            else:
                e = Item(tag, value)
            return e
        func.__name__ = name
        cache[name] = func
    return func

class Item(object):
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

class Element(object):
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

