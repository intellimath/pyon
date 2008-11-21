# The MIT License
#
# Copyright (c) 2008 
# Shibzoukhov Zaur Moukhadinovich
# szport@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import ast
from pyon.resolvers import defaultResolver, customResolver, safeNameResolver

__all__ = ['loads']

null = object()
default = object()
self = object()

class PyonError(Exception): pass
class PyonResolveError(Exception): pass

def _reconstructor(cls, base, state):
    if base is object:
        obj = object.__new__(cls)
    else:
        obj = base.__new__(cls, state)
        if base.__init__ != object.__init__:
            base.__init__(obj, state)
    return obj

method_cache = {}
def cache_method(name):
    def func(m, name=name):
        method_cache[name] = m
        return m
    return func

class NodeTransformer(object):    
    #
    def __init__(self, nameResolver):
        self.cache = {
            'True':True, 'False':False, 
            'object':object, 'type': type, 
            'int':int, 'string':str, 'bool':bool, 'float':float, 'bytes':bytes,
            '_reconstructor':_reconstructor, 'None':None}
        self.nameResolver = nameResolver
        self.assigns = {}
        self.post_actions = []
    #
    def visit(self, astTree):
        return visit(self, astTree)

def visit(self, state):
    method = method_cache.get(state.__class__.__name__, None)
    if method is None:
        raise PyonError('Non supporting AST node ' + state.__class__.__name__)
        
    return method(self, state)
#
@cache_method('Module')
def visit_Module(self, node):
    return [x for x in (visit(self, n) for n in node.body) if x is not null]
#
@cache_method('Expr')
def visit_Expr(self, node):
    return visit(self, node.value)
#
@cache_method('Attribute')
def visit_Attribute(self, node):
    return getattr(visit(self, node.value), node.attr)
#
@cache_method('NoneType')
def visit_NoneType(self, node):
    return None
#
#@cache_method('Compare')
#def visit_Compare(self, node):
#    left = visit(self, node.left)
#    result = True
#    for op, node_right in zip(node.ops, node.comparators):
#        opName = op.__class__.__name__
#        right = visit(self, node_right)
#        #print(opName)
#        if opName == 'Gt':
#            result = result and left > right
#        elif opName == 'Lt':
#            result = result and left < right
#        elif opName == 'LtE':
#            result = result and left <= right
#        elif opName == 'GtE':
#            result = result and left >= right
#        elif opName == 'Eq':
#            result = result and left == right
#        elif opName == 'NotEq':
#            result = result and left != right
#        else:
#            raise PyonException('Unexpected operation ' + opName)
#        left = right
#    return result
#
@cache_method('Assign')
def visit_Assign(self, node):
    name = node.targets[0].id
    value = visit(self, node.value)
    self.cache[name] = value
    self.assigns[name] = value
    return null
#
@cache_method('Tuple')
def visit_Tuple(self, node):
    return tuple(visit(self, el) for el in node.elts)
#
def visit_iter_Sequence(self, node):
    if node.__class__ in (ast.Tuple, ast.List):
        return (visit(self, el) for el in node.elts)
    else:
        return visit(self, node)
#
def visit_iter_Mapping(self, node):
    if node.__class__ is ast.Dict:
        return ((visit(self, key), visit(self, value)) for key, value in zip(node.keys, node.values))
    else:
        return visit(self, node)
#
@cache_method('List')
def visit_List(self, node):
    lst = []
    for i, el in enumerate(node.elts):
        if el.__class__ is ast.Name:
            try:
                lst.append(visit_Name(self, el))
            except PyonResolveError:
                def setitem(lst=lst, i=i, name=el):
                    lst[i] = visit_Name(self, name)
                lst.append(None)
                self.post_actions.append(setitem)
        else:
            lst.append(visit(self, el))
    return lst
#
@cache_method('Subscript')
def visit_Subscript(self, node):
   item = visit(self, node.value)
   key = visit(self, node.slice.value)
   return item[key]
#    
@cache_method('Dict')
def visit_Dict(self, node):
    _dict = {}
    for key, value in zip(node.keys, node.values):
        _key = visit(self, key)
        if value.__class__ is ast.Name:
            try:
                item = visit_Name(self, value)
                _dict[_key] = item
            except PyonResolveError:
                def setitem(map=_dict, key=_key, name=value):
                    print(id(map))
                    map[key] = visit_Name(self, name)
                self.post_actions.append(setitem)
        else:
            _dict[_key] = visit(self, value)
    return _dict    
        
@cache_method('Call')
def visit_Call(self, node):
    callee = visit(self, node.func)

    if node.args:
        args = tuple(visit(self, arg) for arg in node.args)
    else:
        args = ()
    
    instance = callee(*args)
    
    if node.keywords:
        setstate = getattr(instance, '__setstate__', None)
        if setstate:
            state = dict((keyword.arg, visit(self, keyword.value)) for keyword in node.keywords)
            #state = state.get('__pyon_state__', state)
            setstate(state)
        else:
            for keyword in node.keywords:
                valueTree = keyword.value
                if valueTree.__class__ is ast.Name:
                    try:
                        setattr(instance, keyword.arg, visit_Name(self, valueTree))
                    except PyonResolveError:
                        def _setattr(instance=instance, attr=keyword.arg, nameEl=valueTree):
                            setattr(instance, attr, visit_Name(self, nameEl))
                        self.post_actions.append(_setattr)
                else:
                    setattr(instance, keyword.arg, visit(self, valueTree))

    if node.starargs:
        for arg in visit_iter_Sequence(self, node.starargs):
            instance.append(arg)

    if node.kwargs:
        for key, arg in visit_iter_Mapping(self, node.kwargs):
            instance[key] = arg
    
    return instance
#
@cache_method('Num')
def visit_Num(self, node):
    return node.n
#
@cache_method('Name')
def visit_Name(self, node):
    try:
        return self.cache[node.id]
    except:
        pass

    try:
        name = node.id
        ob = self.nameResolver(name)
        self.cache[name] = ob
        return ob
    except:
        raise PyonResolveError("Can't resolve name " + name)
#
@cache_method('Str')
def visit_Str(self, node):
    return node.s
#
@cache_method('Bytes')
def visit_Bytes(self, node):
    return node.s

def loads(source, resolver=None, given={}, safe=False):    

    if safe:
        nameResolver = safeNameResolver
    elif resolver is None:
        nameResolver = defaultResolver(True, given)
    else:
        nameResolver = resolver

    transformer = NodeTransformer(nameResolver)
    if issubclass(type(source), str):
        tree = ast.parse(source)
        ob = visit(transformer, tree)[-1]
    elif issubclass(type(source), ast.AST):
        ob = visit(transformer, source)[-1]
    else:
        PyonError('Source must be a string or AST', source)
    if transformer.post_actions:
        for action in transformer.post_actions:
            action()
    return ob
