#

__all__ = ['dumps']

null = object()

objects_cache = {}
objects_info = {}
NoneType = type(None)

class Cacher(object):

    def visit(self, o):
        if type(o) in (NoneType, int, str, bool, float):
            return
        

        oId = id(o)
        global objects_cache, objects_info
        if oId in objects_cache:
            info = objects_info[oId]
            if info == 0:
                objects_info[oId] = 1
        else:
            objects_cache[oId] = o
            objects_info[oId] = 0
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
            return self.with_not_reduce((newname, newargs, state))
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
    def with_not_reduce(self, state):
        n = len(state)
        if n > 1 and state[1]:
            for item in state[1]:
                self.visit(item)
        if n > 2 and state[2]:
            self.visit(state[2])

class Representor(object):

    def __init__(self, fast=True):
        self.fast = fast
        self.assigns = []
        self.post_assigns = []
        self.reprs = {}

    def visit(self, o):
        if self.fast:
            name = 'visit_' + o.__class__.__name__
            method = getattr(self, name, self.visit_object)
            return method(o)
        else:
            oId = id(o)
            if oId in objects_cache:
                n = self.reprs.get(oId, None)
                if n is None:
                    name = 'visit_' + o.__class__.__name__
                    method = getattr(self, name, self.visit_object)

                    n = len(self.assigns)
                    self.reprs[oId] = n
                    varName = '_p__' + str(n)

                    oRepr = method(o)

                    self.assigns.append(varName + "=" + oRepr)
                    return varName
                else:
                    varName = '_p__' + str(n)
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
        if self.fast:
            return '[' + ','.join(self.visit(item) for item in o) + ']'
        else:
            oId = id(o)
            if oId in objects_cache:
                n0 = self.reprs[id(o)]
                lst = []
                lst_cache = {}
                for i,item in enumerate(o):
                    itemId = id(item)
                    if itemId in objects_cache:
                        lst.append(None)
                        lst_cache[i] = itemId
                    else:
                        lst.append(item)
                oRepr = '[' + ','.join(self.visit(item) for item in lst) + ']'
                if lst_cache:
                    for i, itemId in lst_cache.items():
                        n = self.reprs[itemId]
                        self.post_assigns.append("_p__" + str(n0) + "[" + str(i) + "]=" +  "_p__" + str(n))
                return oRepr
            else:
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
        if self.fast:
            return '{' + ','.join(self.visit(key) + ':' + self.visit(item) for key,item in o.items()) + '}'
        else:
            oId = id(o)
            if oId in objects_cache:
                n0 = self.reprs[id(o)]
                _dict = {}
                dict_cache = []
                for i,item in o.items():
                    itemId = id(item)
                    if itemId in objects_cache:
                        #_dict[i] = None
                        key = self.visit
                        dict_cache.append((i, itemId))
                    else:
                        _dict[i] = item
                oRepr = '{' + ','.join(self.visit(key) + ':' + self.visit(item) for key,item in _dict.items()) + '}'
                if dict_cache:
                    for i, itemId in dict_cache:
                        key = self.visit(i)
                        n = self.reprs[itemId]
                        self.post_assigns.append("_p__" + str(n0) + "[" + key + "]=" +  "_p__" + str(n))
                return oRepr
            else:
                return '{' + ','.join(self.visit(key) + ':' + self.visit(item) for key,item in o.items()) + '}'
    
    def visit_object(self, o):
        if  hasattr(o, '__reduce__'):
            #print(o)
            state = o.__reduce__()
            factory = state[0]
            factoryType = factory.__class__
            cls = o.__class__
            if factoryType.__module__ == 'builtins':
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
                        name = factoryType.__module__ + '.' + factory.__name__
                else:
                    if factory.__module__ == '__main__':
                        name = factory.__name__
                    else:
                        name = factory.__module__ + '.' + factory.__name__
            return self.with_reduce((name,) + state[1:])
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
            return self.with_not_reduce((newname, newargs, state))
    #
    def with_reduce(self, state):
        n = len(state)
        ret = ''
        if n > 0:
            ret += state[0] + '('
        if n > 1 and state[1]:
            ret += ','.join(self.visit(item) for item in state[1]) + ','
        if n > 2 and state[2]:
            if isinstance(state[2], dict):
                ret += ','.join('%s=%s' % (k, self.visit(v)) for k, v in state[2].items()) + ','
            else:
                ret += self.visit(state) + ','
        if n > 3 and state[3]:
            ret += '*[' + ','.join(self.visit(v) for v in state[3]) + ']'
        if n > 4 and state[4]:
            ret += '**{' + ','.join('%s:%s' % (self.visit(k), self.visit(v)) for k, v in state[4].items()) + '}'
        if ret[-1] == ',':
            ret = ret[:-1]
        ret += ')'
        return ret
    #
    def with_not_reduce(self, state):
        n = len(state)
        ret = ''
        if n > 0:
            ret += state[0] + '('
        if n > 1 and state[1]:
            ret += ','.join(self.visit(item) for item in state[1]) + ','
        if n > 2 and state[2]:
            ret += self.visit(state[2]) + ','
        if ret[-1] == ',':
            ret = ret[:-1]
        ret += ')'
        return ret

def dumps(o, fast=True):
    if not fast:
        cacher = Cacher()
        cacher.visit(o)
        global objects_info, objects_cache
        objects_info = {oId:n for oId,n in objects_info.items() if n > 0}
        objects_cache = {oId:o for oId,o in objects_cache.items() if oId in objects_info}
    representor = Representor(fast)
    text = representor.visit(o)
    if representor.assigns:
        assigns = "\n".join(representor.assigns)
    else:
        assigns = ""
    if representor.post_assigns:
        post_assigns = "\n".join(representor.post_assigns)
    else:
        post_assigns = ""
    return "\n".join(s for s in [assigns,post_assigns,text] if s)
