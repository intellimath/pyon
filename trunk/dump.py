#

from copyreg import dispatch_table
from pyon import dumpcache

__all__ = ['dumps']

null = object()

NoneType = type(None)

method_cache = {}
def cache_method(name):
    def func(m, name=name):
        method_cache[name] = m
        return m
    return func
    
MODULE_NAMES = ('__cache__', '__main__', '__builtin__', 'builtins')

class DumpContext(object):

    def __init__(self, fast=False, classdef=False, given=None, prefix='_p__', pretty=False):
        self.fast = fast
        self.classdef = classdef
        self.assigns = []
        self.pretty = pretty
        self.nl = pretty and '\n' or ''
        self.reprs = {}
        self.typeNames = {}
        self.prefix = prefix
        if given:
            self.given = dict((id(o),name) for name, o in given.items())
        else:
            self.given = {}

def visit(self, o, offset, start=None):
    if isinstance(o, type):
        return visit_type(self, o, offset, start)

    if start is None:    
        real_offset = self.nl + offset
    else:
        real_offset = start
        
    if self.fast:
        method = method_cache.get(o.__class__.__name__, visit_object) 
        return real_offset + method(self, o, offset, start)
    else:
        oId = id(o)
        if oId in self.objects_cache:
            varName = self.reprs.get(oId, None)
            if varName is None:
                method = method_cache.get(o.__class__.__name__, visit_object)

                n = len(self.assigns)
                varName = self.given.get(oId, self.prefix + str(n))
                self.reprs[oId] = varName

                oRepr = method(self, o, offset, start)

                self.assigns.append(varName + "=" + oRepr)
            return real_offset + varName
        else:
            method = method_cache.get(o.__class__.__name__, visit_object) 
            return real_offset + method(self, o, offset, start)
#
@cache_method('NoneType')
def visit_NoneType(self, o, offset, start=None):
    return 'None'
#
@cache_method('int')
def visit_int(self, o, offset, start=None):
    return repr(o)
#
@cache_method('long')
def visit_long(self, o, offset, start=None):
    return repr(o)
#
@cache_method('property')
def visit_property(self, o, offset, start=None):
    items = [f for f in (o.fget, o.fset, o.fdel, o.__doc__) if f is not None]
    return 'property(' + dump_items(self, items, offset, '') + ')'
#
@cache_method('str')
def visit_str(self, o, offset, start=None):
    return repr(o)
#
@cache_method('bool')
def visit_bool(self, o, offset, start=None):
    return repr(o)
#
@cache_method('float')
def visit_float(self, o, offset, start=None):
    return repr(o)
#
@cache_method('bytes')
def visit_bytes(self, o, offset, start=None):
    return repr(o)
#
@cache_method('list')
def visit_list(self, o, offset, start=None):
    offset1 = self.pretty and offset + ' ' or ''
    return '[' + dump_items(self, o, offset1).lstrip() + ']'
#
@cache_method('tuple')
def visit_tuple(self, o, offset, start=None):
    offset1 = self.pretty and offset + ' ' or ''
    if len(o) == 1:
        return '(' + visit(self, o[0], offset1).lstrip() + ',)'
    else:
        return '(' + dump_items(self, o, offset1).lstrip() + ')'
#
@cache_method('dict')
def visit_dict(self, o, offset, start=None):
    offset1 = self.pretty and offset + ' ' or ''
    return '{' + dump_mapping(self, o, offset1).lstrip() + '}'
#
def dump_items(self, items, offset, start=None):
    return ','.join(visit(self, item, offset, start) for item in items)
#
def dump_mapping(self, mapping, offset, start=None):
    return ','.join(visit(self, k, offset) + ':' + visit(self, v, offset, '') for k, v in mapping.items())
#
def dump_kwitems(self, kwitems, offset, start=None):
    if start is None:    
        real_offset = self.nl + offset
    else:
        real_offset = start
    return ','.join(real_offset + k+'='+visit(self, v, offset, '') for k, v in kwitems.items())
#
@cache_method('function')
def visit_function(self, o, offset, start=None):
    if o.__module__ in MODULE_NAMES:
        name = o.__name__
    else:
        name = o.__module__ + '.' + o.__name__
    return name
#
@cache_method('method')
def visit_method(self, o, offset, start=None):
    return visit(self, o.__self__, offset, start) + "." + o.__func__.__name__
#
@cache_method('builtin_function_or_method')
def visit_builtin_function_or_method(self, o, offset, start=None):
    if o.__module__ in MODULE_NAMES:
        name = o.__name__
    else:
        name = o.__module__ + '.' + o.__name__
    return name
#
@cache_method('type')
def visit_type(self, o, offset, start=None):
    if not self.classdef:
        if o.__module__ in MODULE_NAMES:
            name = o.__name__
        else:
            name = o.__module__ + '.' + o.__name__
        return name

    offset1 = self.pretty and offset + '  ' or ''
        
    try:
        metatype = o.__metaclass__
    except:
        metatype =  o.__class__

    if metatype == type:
        return o.__name__
    else:
        factory = metatype
        args = (o.__name__, o.__bases__)

        if factory.__module__ in MODULE_NAMES:
            name = factory.__name__
        else:
            if isinstance(factory, type):
                name = factory.__module__ + '.' + factory.__name__
            else:
                name = factory.__class__.__module__ + '.' + factory.__name__
                
        ret = name + '('
        if args:
            ret += dump_items(self, args, offset1) + ','

        kwargs = dict(o.__dict__)
        kwargs.pop('__dict__')
        kwargs.pop('__weakref__')
        if '__metaclass__' in kwargs:
            kwargs.pop('__metaclass__')

        if kwargs:
            if '__module__' in kwargs:
                kwargs.pop('__module__')
            if kwargs['__doc__'] is None:
                kwargs.pop('__doc__')
            ret += dump_kwitems(self, kwargs, offset1)
        if ret[-1] == ',':
            ret = ret[:-1]
        ret += ')'
        return ret
#
@cache_method('object')
def visit_object(self, o, offset, start=None):

    oId = id(o)
    reduce = dispatch_table.get(type(o))
    if reduce:
        rv = reduce(obj)
    
    reduce = getattr(o, '__reduce_ex__', None)
    if reduce:
        state = reduce(3)
        return with_reduce(self, o, state, offset, start)
    else:
        reduce = getattr(o, '__reduce__', None)
        if reduce:
            state = reduce()
            return with_reduce(self, o, state, offset, start)
        else:
            return without_reduce(self, o, offset, start)
#
def with_reduce(self, o, state, offset, start=None):
    name = visit(self, state[0], offset)
    offset1 = self.pretty and offset + '  ' or ''
    if start is None:    
        real_offset = self.nl + offset1
    else:
        real_offset = offset + start

    n = len(state)
    ret = ''
    if n > 0:
        ret += name + '('
    if n > 1:
        if state[1]:
            ret += dump_items(self, state[1], offset1) + ','
        if n > 2:
            if state[2]:
                ret += dump_kwitems(self, state[2], offset1) +','
            if n > 3:
                if state[3]:
                    offset2 = self.pretty and offset1 + '  ' or ''
                    ret += real_offset + '*[' + dump_items(self, state[3], offset2).lstrip() + '],'
                if n > 4:
                    if state[4]:
                        offset3 = self.pretty and offset1 + '   ' or ''
                        ret += real_offset + '**{' + dump_mapping(self, state[4], offset3) + '}'
    if ret[-1] == ',':
        ret = ret[:-1]
    ret += ')'
    return ret
#
def without_reduce(self, o, offset=None):
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

    offset1 = self.pretty and offset + '  ' or ''
    n = len(state)
    ret = ''
    if n > 0:
        ret += state[0] + '('
    if n > 1 and state[1]:
        ret += dump_items(self, state[1], offset1) + ','
    if n > 2 and state[2]:
        ret += '*'+ visit(self, state[2], offset1).lstrip() + ','
    if ret[-1] == ',':
        ret = ret[:-1]
    ret += ')'
    return ret

def dumps(o, fast=False, classdef=False, pretty=False, given=None):
    if not fast:
        cacher = dumpcache.Cacher()
        dumpcache.visit(cacher, o)
        objects_info = dict((oId,n) for oId,n in cacher.objects_info.items() if n > 0)
        objects_cache = dict((oId,o) for oId,o in cacher.objects_cache.items() if oId in objects_info)
    context = DumpContext(fast=fast, classdef=classdef, given=given, pretty=pretty)
    if not fast:
        context.objects_cache = objects_cache
        
    text = visit(context, o, '').lstrip()
    if context.assigns:
        assigns = "\n".join(context.assigns)
    else:
        assigns = ""
    return "\n".join(s for s in [assigns,text] if s)
