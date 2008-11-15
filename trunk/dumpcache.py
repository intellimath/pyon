#! coding: utf-8

NoneType = type(None)

class Cacher(object):
    #
    def __init__(self):
        self.objects_cache = {}
        self.objects_info = {}

method_cache = {}
def cache_method(name):
    def func(m, name=name):
        method_cache[name] = m
        return m
    return func

def visit(self, o):
    if type(o) in (NoneType, int, str, bool, float):
        return
    
    #if isinstance(o, type):
    #    visit_type(self, o)
    #    return
    
    oId = id(o)
    if oId in self.objects_cache:
        info = self.objects_info[oId]
        if info == 0:
            self.objects_info[oId] = 1
    else:
        self.objects_cache[oId] = o
        self.objects_info[oId] = 0
        method = method_cache.get(o.__class__.__name__, visit_object) 
        method(self, o)
#
@cache_method('list')
def visit_list(self, o):
    for item in o:
        visit(self, item)
#
@cache_method('tuple')
def visit_tuple(self, o):
    for item in o:
        visit(self, item)
#
@cache_method('object')
def visit_object(self, o):
    return
#
@cache_method('type')
def visit_type(self, o):
    metatype = o.__class__
    if metatype == type:
        return
    else:
        return
#
@cache_method('dict')
def visit_dict(self, o):
    for key,item in o.items():
        visit(self, key)
        visit(self, item)

@cache_method('property')
def visit_property(self, o):
    for f in (o.fget, o.fset, o.fdel, o.__doc__): 
        if f is not None:
            visit(self, f) 

@cache_method('function')
def visit_function(self, o):
    return
#
@cache_method('method')
def visit_method(self, o):
    return visit(self, o.__self__)
#
@cache_method('builtin_function_or_method')
def visit_builtin_function_or_method(self, o):
    return
        
@cache_method('object')
def visit_object(self, o):
    if isinstance(o, type):
        return visit_type(self, o)
        
    reduce = getattr(o, '__reduce__', None)
    if reduce:
        state = reduce()
        return with_reduce(self, state)
    else:
        newname = o.__class__.__name__
        
        newargs = None
        getnewargs = getattr(o, '__getnewargs__', None)
        if getnewargs:
            newargs = getnewargs()
        
        state = None
        getstate = getattr(o, '__getstate__', None)
        if getstate:
            state = getstate()
        else:
            state = getattr(o, '__dict__', None)
            if state is None:
                state = {}
                for name in o.__slots__:
                    value = getattr(o, name, null)
                    if value is not null:
                        state[name] = value
        return without_reduce(self, newargs, state)
#
def with_reduce(self, state):
    visit(self, state[0])
    n = len(state)
    if n > 1:
        if state[1]:
            for item in state[1]:
                visit(self, item)
        if n > 2:
            if state[2]:
                for k, v in state[2].items():
                    visit(self, v)
            if n > 3:
                if state[3]:
                    for v in state[3]:
                        visit(self, v)
                if n > 4:
                    if state[4]:
                        for k, v in state[4].items():
                            visit(self, k)
                            visit(self, v)
#
def without_reduce(self, args, state):
    if args:
        for item in args:
            visit(self, item)
    if state:
        visit(self, state)
