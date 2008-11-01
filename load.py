#
import sys
import ast
from pyon.resolvers import defaultResolver, customResolver
import time

__all__ = ['loads']

null = object()
default = object()
self = object()

class PyonError(Exception): pass

def _reconstructor(cls, base, state):
    if base is object:
        obj = object.__new__(cls)
    else:
        obj = base.__new__(cls, state)
        if base.__init__ != object.__init__:
            base.__init__(obj, state)
    return obj

def IF(self, condTree, trueTree, falseTree = None, **kwargs):
    if self.visit(condTree):
        return self.visit(trueTree)
    elif falseTree is not None:
        return self.visit(falseTree)

def CASE(self, valueTree, casesTree, defaultTree = None):
    value = self.visit(valueTree)
    for keyTree, tree in casesTree.items():
        if self.visit(keyTree) == value:
            return self.visit(tree)
    if default is not None:
        return self.visit(defaultTree)

method_cache = {}
def cache_method(name):
    def func(m, name=name):
        method_cache[name] = m
        return m
    return func

class NodeTransformer(object):    
    #
    def __init__(self, nameResolver):
        self.cache = {'True':True, 'False':False, 'object':object, 'type': type, '_reconstructor':_reconstructor, 'None':None, 'IF':IF, 'CASE':CASE}
        self.nameResolver = nameResolver
    #
    def visit(self, state):
        name = state.__class__.__name__
        method = method_cache[name]
        return method(self, state)
    #
    @cache_method('Module')
    def visit_Module(self, node):
        return [x for x in (self.visit(n) for n in node.body) if x is not null]
    #
    @cache_method('Expr')
    def visit_Expr(self, node):
        return self.visit(node.value)
    #
    @cache_method('Attribute')
    def visit_Attribute(self, node):
        return getattr(self.visit(node.value), node.attr)
    #
    @cache_method('NoneType')
    def visit_NoneType(self, node):
        return None
    #
    @cache_method('Compare')
    def visit_Compare(self, node):
        left = self.visit(node.left)
        result = True
        for op, node_right in zip(node.ops, node.comparators):
            opName = op.__class__.__name__
            right = self.visit(node_right)
            #print(opName)
            if opName == 'Gt':
                result = result and left > right
            elif opName == 'Lt':
                result = result and left < right
            elif opName == 'LtE':
                result = result and left <= right
            elif opName == 'GtE':
                result = result and left >= right
            elif opName == 'Eq':
                result = result and left == right
            elif opName == 'NotEq':
                result = result and left != right
            else:
                raise PyonException('Unexpected operation ' + opName)
            left = right
        return result
    #
    @cache_method('Assign')
    def visit_Assign(self, node):
        name = node.targets[0].id
        value = self.visit(node.value)
        self.cache[name] = value
        return null
    #
    @cache_method('Tuple')
    def visit_Tuple(self, node):
        return tuple(self.visit(el) for el in node.elts)
    #
    @cache_method('List')
    def visit_List(self, node):
        return [self.visit(el) for el in node.elts]
    #
    @cache_method('Subscript')
    def visit_Subscript(self, node):
       item = self.visit(node.value)
       key = self.visit(node.slice.value)
       return item[key]
    #    
    @cache_method('Dict')
    def visit_Dict(self, node):
        return dict((self.visit(key),self.visit(value)) for key,value in zip(node.keys, node.values))
        
    def visit_pyon(self, callee, *args, **kwargs):
        if callee == IF:
            return IF(self, *args, **kwargs)
        elif callee == CASE:
            return CASE(self, *args, **kwargs)
        
    @cache_method('Call')
    def visit_Call(self, node):
        callee = self.visit(node.func)
        
        if callee in (IF,CASE):
           args = ()
           kwargs = {}
           if node.args:
               args = tuple(arg for arg in node.args)
           if node.keywords:
               kwargs = dict((keyword.arg,keyword.value) for keyword in node.keywords)
           return self.visit_pyon(callee, *args, **kwargs)
       
        if node.args:
            args = tuple(self.visit(arg) for arg in node.args)
        else:
            args = ()
        
        instance = callee(*args)
        
        if node.keywords:
            setstate = getattr(instance, '__setstate__', None)
            if setstate:
                state = dict((keyword.arg, self.visit(keyword.value)) for keyword in node.keywords)
                #state = state.get('__pyon_state__', state)
                setstate(state)
            else:
                for keyword in node.keywords:
                    setattr(instance, keyword.arg, self.visit(keyword.value))

        if node.starargs:
            starargs = self.visit(node.starargs)
            for arg in starargs:
                instance.append(arg)

        if node.kwargs:
            starkwargs = self.visit(node.kwargs)
            for key,arg in starkwargs.items():
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
            raise RuntimeError("Can't resolve name " + name)
    #
    @cache_method('Str')
    def visit_Str(self, node):
        return node.s

def loads(source, __resolver__=None, __modules__ = True, **kwargs):    
        
    if __resolver__ is None:
        nameResolver = defaultResolver(modules = __modules__, **kwargs)
    elif type(__resolver__) == dict:
        nameResolver = dictResolver(__resolver__, modules = __modules__, **kwargs)
    else:
        nameResolver = customResolver(__resolver__, modules = __modules__, **kwargs)
        
    transformer = NodeTransformer(nameResolver)
    if issubclass(type(source), str):
        tree = ast.parse(source)
        return transformer.visit(tree)[-1]
    elif issubclass(type(source), ast.AST):
        return transformer.visit(source)[-1]
    else:
        PyonError('Source must be a string or AST', source)
