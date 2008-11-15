#
import sys

def defaultResolver(use_modules = True, given={}):
    _dict = dict(sys._getframe(2).f_globals)
    _dict.update(sys._getframe(2).f_locals)
    if given:
        _dict.update(given)
    return dictResolver(_dict, use_modules)
    
def dictResolver(_dict, use_modules=True):
        if use_modules:
            def resolver(name):
                try:
                    return _dict[name]
                except: pass
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                return _dict[name]
            return resolver

def customResolver(nameResolver, use_modules=True, given={}):
    localsDict = dict(given)
    if localsDict:
        if use_modules:
            def resolver(name):
                try:
                    return nameResolver(name)
                except: pass
                try:
                    return localsDict[name]
                except: pass
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                try:
                    return nameResolver(name)
                except: pass
                try:
                    return localsDict[name]
                except: pass
            return resolver
    else:
        if use_modules:
            def resolver(name):
                return nameResolver(name)
                return sys.modules[name]
            return resolver
        else:
            return nameResolver

safe_cache = {}
def safeNameResolver(name):
    C = safe_cache.get(name, None)
    if C is None:
        C = safe_cache[name] = type(name, (_Element_,), {'__module__' : '__cache__'})
    return C

class _Element_(object):
    #
    def __init__(self, *args):
        self._args__ = args
        self._sequence__ = []
        self._mapping__ = {}
    #
    @property
    def tag(self):
        return self.__class__.__name__
    #
    @property
    def args(self):
        return self.__args
    #
    @property
    def sequence(self):
        return self.__sequence
    #
    @property
    def mapping(self):
        return self.__mapping
    #
    def append(self, item):
        self.sequence.append(item)
    #
    def __setitem__(self, key, item):
        self.mapping[key] = item
    #
    def __reduce__(self):
        _dict = dict(self.__dict__)
        args = _dict.pop('_args__', None)
        sequence = _dict.pop('_sequence__', None)
        mapping = _dict.pop('_mapping__', None)
        return safeNameResolver(self.__class__.__name__), args, _dict, sequence, mapping
    #
    def __setstate__(self, kwargs):
        self.__dict__.update(kwargs)
