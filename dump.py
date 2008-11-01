#

__all__ = ['dumps']

null = object()

class Representor(object):

    def visit(self, o):
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
    
    def visit_object(self, o):
        if  hasattr(o, '__reduce__'):
            #print(o)
            state = o.__reduce__()
            factory = state[0]
            factoryType = factory.__class__
            cls = o.__class__
            if factoryType.__module__ == 'builtins':
                if isinstance(factory, type):
                    name = cls.__module__ + '.' + cls.__name__
                else:
                    name = factory.__name__
            else:
                if isinstance(factory, type):
                    name = factoryType.__module__ + '.' + factory.__name__
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

def dumps(o):
    representor = Representor()
    return representor.visit(o)
