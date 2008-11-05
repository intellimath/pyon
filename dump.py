#

__all__ = ['dumps']

null = object()

#reprs = {}
NoneType = type(None)

class Cacher(object):

    def __init__(self):
        self.objects_cache = {}
        self.objects_info = {}

    def visit(self, o):
        if type(o) in (NoneType, int, str, bool, float):
            return
        oId = id(o)
        if oId in self.objects_cache:
            info = self.objects_info[oId]
            if info == 0:
                self.objects_info[oId] = 1
        else:
            self.objects_cache[oId] = o
            self.objects_info[oId] = 0
            name = 'visit_' + o.__class__.__name__
            method = getattr(self, name, self.visit_object)
            method(o)
    #
    def visit_list(self, o):
        for item in o:
            self.visit(item)
    #
    def visit_tuple(self, o):
        for item in o:
            self.visit(item)
    #
    def visit_object(self, o):
        return
    #
    def visit_type(self, o):
        return
    #
    def visit_dict(self, o):
        for key,item in o.items():
            self.visit(key)
            self.visit(item)
    
    def visit_object(self, o):
        if  hasattr(o, '__reduce__'):
            state = o.__reduce__()
            return self.with_reduce(state)
        else:
            newname = o.__class__.__name__
            
            newargs = None
            if hasattr(o, '__getnewargs__'):
                newargs = o.__getnewargs__()
            
            state = None
            if hasattr(o, '__getstate__'):
                state = o.__getstate__()
            else:
                if hasattr(o, '__dict__'):
                    state = o.__dict__
                else:
                    state = {}
                    for name in o.__slots__:
                        value = getattr(o, name, null)
                        if value is not null:
                            state[name] = value
            return self.without_reduce((newname, newargs, state))
    #
    def with_reduce(self, state):
        n = len(state)
        if n > 1 and state[1]:
            for item in state[1]:
                self.visit(item)
        if n > 2 and state[2]:
            if isinstance(state[2], dict):
                for k, v in state[2].items():
                    self.visit(v)
            else:
                self.visit(state)
        if n > 3 and state[3]:
            for v in state[3]:
                self.visit(v)
        if n > 4 and state[4]:
            for k, v in state[4].items():
                self.visit(k)
                self.visit(v)
    #
    def without_reduce(self, state):
        n = len(state)
        if n > 1 and state[1]:
            for item in state[1]:
                self.visit(item)
        if n > 2 and state[2]:
            self.visit(state[2])

class Representor(object):

    def __init__(self, fast=True, given=None):
        self.fast = fast
        self.assigns = []
        #self.post_assigns = []
        self.reprs = {}
        if given:
            self.kwargs = dict((id(o),name) for name, o in given.items())
        else:
            self.kwargs = {}

    def visit(self, o):
        if self.fast:
            name = 'visit_' + o.__class__.__name__
            method = getattr(self, name, self.visit_object)
            return method(o)
        else:
            oId = id(o)
            if oId in self.objects_cache:
                varName = self.reprs.get(oId, None)
                if varName is None:
                    name = 'visit_' + o.__class__.__name__
                    method = getattr(self, name, self.visit_object)

                    n = len(self.assigns)
                    varName = self.kwargs.get(oId, '_p__' + str(n))
                    self.reprs[oId] = varName

                    oRepr = method(o)

                    self.assigns.append(varName + "=" + oRepr)
                return varName
            else:
                name = 'visit_' + o.__class__.__name__
                method = getattr(self, name, self.visit_object)
                return method(o)
    #
    def visit_NoneType(self, o):
        return 'None'
    #
    def visit_int(self, o):
        return repr(o)
    #
    def visit_str(self, o):
        return repr(o)
    #
    def visit_bool(self, o):
        return repr(o)
    #
    def visit_float(self, o):
        return repr(o)
    #
    def visit_list(self, o):
        return '[' + ','.join(self.visit(item) for item in o) + ']'
    #
    def visit_tuple(self, o):
        return '(' + ','.join(self.visit(item) for item in o) + ')'
    #
    def visit_object(self, o):
        return 'object'
    #
    def visit_type(self, o):
        return o.__name__
    #
    def visit_dict(self, o):
        return '{' + ','.join(self.visit(key) + ':' + self.visit(item) for key,item in o.items()) + '}'
    #
    def visit_object(self, o):
        oId = id(o)
        if  hasattr(o, '__reduce__'):
            #print(o)
            state = o.__reduce__()        
            return self.with_reduce(o, state)
        elif hasattr(o, '__reduce_ex__'):
            try:
                state = o.__reduce_ex__(3)
                return self.with_reduce(o, state)
            except:
                pass

            try:
                state = o.__reduce_ex__(2)
                return self.with_reduce(o, state)
            except:
                pass
        else:
            return self.without_reduce(o)
    #
    def with_reduce(self, o, state):
        factory = state[0]
        factoryClass = factory.__class__
        cls = o.__class__
        if isinstance(factory, type):
            if factory.__module__ in ('__main__', '__builtins__'):
                name = factory.__name__
            else:
                name = factory.__module__ + '.' + factory.__name__
        else:
            if factory.__module__ in ('__main__', '__builtins__'):
                name = factory.__name__
            else:
                name = factoryClass.__module__ + '.' + factory.__name__
        '''
        if factoryClass.__module__ == 'builtins':
            if isinstance(factory, type):
                if cls.__module__ == '__main__':
                    name = cls.__name__
                else:
                    name = cls.__module__ + '.' + cls.__name__
            else:
                name = factory.__name__
        else:
            if isinstance(factory, type):
                if factoryType.__module__ == '__main__':
                    name = factory.__name__
                else:
                    name = factoryClass.__module__ + '.' + factory.__name__
            else:
                if factory.__module__ == '__main__':
                    name = factory.__name__
                else:
                    name = factory.__module__ + '.' + factory.__name__
       '''
        n = len(state)
        ret = ''
        if n > 0:
            ret += name + '('
        if n > 1 and state[1]:
            ret += ','.join(self.visit(item) for item in state[1]) + ','
        if n > 2 and state[2]:
            if isinstance(state[2], dict):                
                #if self.fast:
                ret += ','.join('%s=%s' % (k, self.visit(v)) for k, v in state[2].items()) +','
                #else:
                #    ret += self._with_kwargs(o, state[2]) + ','
            else:
                ret += self.visit(state) + ','
        if n > 3 and state[3]:
            #ret += '*' + self.visit(state[3])
            ret += '*[' + ','.join(self.visit(v) for v in state[3]) + ']'
        if n > 4 and state[4]:
            #ret += '**' + self.visit(state[4])
            ret += '**{' + ','.join('%s:%s' % (self.visit(k), self.visit(v)) for k, v in state[4].items()) + '}'
        if ret[-1] == ',':
            ret = ret[:-1]
        ret += ')'
        return ret
    #
    # def _with_kwargs(self, o, state):
        # oId = id(o)
        # if oId in objects_cache:
            # oRepr = ','.join('%s=%s' % (k,self.visit(item)) for k,item in state.items())
            # return oRepr
        # else:
            # return ','.join('%s=%s' % (k, self.visit(v)) for k, v in state.items())
    #
    def without_reduce(self, o):
        clsname = o.__class__.__name__
        
        newargs = None
        if hasattr(o, '__getnewargs__'):
            newargs = o.__getnewargs__()
        
        state = None
        if hasattr(o, '__getstate__'):
            state = o.__getstate__()
        else:
            if hasattr(o, '__dict__'):
                state = o.__dict__
            else:
                state = {}
                for name in o.__slots__:
                    value = getattr(o, name, null)
                    if value is not null:
                        state[name] = value
        n = len(state)
        ret = ''
        if n > 0:
            ret += state[0] + '('
        if n > 1 and state[1]:
            ret += ','.join(self.visit(item) for item in state[1]) + ','
        if n > 2 and state[2]:
            ret += '*'+self.visit(state[2]) + ','
        if ret[-1] == ',':
            ret = ret[:-1]
        ret += ')'
        return ret

def dumps(o, fast=True, given=None):
    if not fast:
        cacher = Cacher()
        cacher.visit(o)
        objects_info = dict((oId,n) for oId,n in cacher.objects_info.items() if n > 0)
        objects_cache = dict((oId,o) for oId,o in cacher.objects_cache.items() if oId in objects_info)
    representor = Representor(fast, given)
    if not fast:
        representor.objects_cache = objects_cache
    text = representor.visit(o)
    if representor.assigns:
        assigns = "\n".join(representor.assigns)
    else:
        assigns = ""
    #if representor.post_assigns:
    #    post_assigns = "\n".join(representor.post_assigns)
    #else:
    #    post_assigns = ""
    return "\n".join(s for s in [assigns,text] if s)
