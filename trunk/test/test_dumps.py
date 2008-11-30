#
import pyon
import ast
import sys
from decimal import Decimal

py_version = sys.version_info[0]*10+sys.version_info[1]
print(py_version)

def assertEqual(expected, result):
    if expected != result:
        print('*** Expected: ', expected, ' Result: ', result)

def test_int():
    assertEqual('17', pyon.dumps(17))
    assertEqual('-17', pyon.dumps(-17))

#def test_float():
#    assertEqual('3.14', pyon.dumps(3.14))
#    assertEqual('-3.14', pyon.dumps(-3.14))

def test_bool():
    assertEqual('True', pyon.dumps(True))
    assertEqual('False', pyon.dumps(False))

def test_bytes():
    assertEqual("b'abs'", pyon.dumps(b'abs'))

def test_long():
    assertEqual('1000000000000000', pyon.dumps(1000000000000000))

def test_Decimal():
    assertEqual("decimal.Decimal('3.14')", pyon.dumps(Decimal('3.14')))
    assertEqual("decimal.Decimal('-3.14')", pyon.dumps(Decimal('-3.14')))
    assertEqual(
        "[decimal.Decimal('-3.14'),decimal.Decimal('3.14')]",
        pyon.dumps([Decimal('-3.14'),Decimal('3.14')], given={'decimal':Decimal}))

def test_string():
    assertEqual("'abs'", pyon.dumps('abs'))

def test_list():
    assertEqual("[1,'abc',True]", pyon.dumps([1, 'abc', True]))
    assertEqual("[]", pyon.dumps([]))

def test_tuple():
    assertEqual("(1,'abc',True)", pyon.dumps((1, 'abc', True)))
    assertEqual("(1,)", pyon.dumps((1,)))
    assertEqual("()", pyon.dumps(()))

def test_set():
    assertEqual("{True,2,'abc',(1,2,3)}", pyon.dumps({True,2,'abc',(1,2,3)}))
    assertEqual("set()", pyon.dumps(set()))

def test_frozenset():
    assertEqual("frozenset([True,2,'abc',(1,2,3)])", pyon.dumps(frozenset([True,2,'abc',(1,2,3)])))
    assertEqual("frozenset()", pyon.dumps(frozenset()))

def test_dict():
    assertEqual("{'a':1,(1,2):True,'abc':3}", pyon.dumps({'a': 1, 'abc': 3, (1, 2): True}))
    assertEqual("{}", pyon.dumps({}))

def test_with_assigns1():
    p1 = (1,2)
    p2 = [1,2]
    assertEqual("p1=(1,2)\np2=[1,2]\n[p1,p2,p1,p2]", pyon.dumps([p1,p2,p1,p2]))
    assertEqual("[(1,2),[1,2],(1,2),[1,2]]", pyon.dumps([p1,p2,p1,p2], fast=True))

def test_with_assigns1_1():
    p1 = (1,2)
    p2 = [1,2]
    assertEqual("[(1,2),[1,2]]", pyon.dumps([p1,p2]))
    assertEqual("[(1,2),[1,2],(1,2),[1,2]]", pyon.dumps([p1,p2,p1,p2], fast=True))

def test_with_assigns2():
    lst = ['foo']
    lst.append(lst)
    assertEqual("lst=['foo',lst]\nlst", pyon.dumps(lst))

def test_with_assigns3():
    p1 = (1,2)
    p2 = [1,2]
    assertEqual(
        "p1=(1,2)\np2=[1,2]\n{'a':p1,'c':p1,'b':p2,'d':p2}",
        pyon.dumps({'a':p1,'b':p2,'c':p1,'d':p2}))

def test_with_assigns3_1():
    p1 = (1,2)
    p2 = [1,2]
    assertEqual(
        "p1=(1,2)\np2=[1,2]\n{'a':p1,'c':p1,'b':p2,'d':p2}",
        pyon.dumps({'a':p1,'b':p2,'c':p1,'d':p2}, given={'p1':p1, 'p2':p2}))

def test_with_assigns4():
    d = {'a':'foo'}
    d['b'] = d
    assertEqual(
        "d={'a':'foo','b':d}\nd",
        pyon.dumps(d, given={'d':d}))

def test_with_assigns4_1():
    d = {'a':'foo'}
    d['b'] = d
    assertEqual(
        "d={'a':'foo','b':d}\nd",
        pyon.dumps(d))

def test_with_assigns5():
    d = ['foo']
    e = ['bar']
    d.append(e)
    e.append(d)
    assertEqual(
        "d=['foo',e]\ne=['bar',d]\n[e,d]",
        pyon.dumps([e,d], given={'d':d,'e':e}))

def test_class1():
    class C(object):
        def __reduce__(self):
            return C, (), self.__dict__

    c= C()
    assertEqual("C()", pyon.dumps(c))


def test_recursive_class():
    class C(object):
        def __reduce__(self):
            return C, (), self.__dict__

    c= C()
    c.parent = c
    assertEqual("c=C(parent=c)\nc", pyon.dumps(c))


def test_class2():
    class C(object):
        def __reduce__(self):
            return C, (), self.__dict__

    c = C()
    c.a = 1
    c.b = 'python'
    c.c = [1,2]
    assertEqual("C(a=1,c=[1,2],b='python')", pyon.dumps(c))
    print(pyon.dumps(c, pretty=True))


def test_class3():
    class C(list):
        def __reduce__(self):
            return C, (), self.__dict__, list(self)

    c = C()
    c.a = 1
    c.b = 2
    c.extend(['a','b','c'])
    assertEqual("C(a=1,b=2,*['a','b','c'])", pyon.dumps(c))
    print(pyon.dumps(c, pretty=True))


def test_class4():
    class Element(object):
        def __init__(self, tag):
            self._tag = tag
            self._children = []
        def __setstate__(self, state):
            self.__dict__.update(state)
        def append(self, e):
            self._children.append(e)
        def __reduce__(self):
            _dict = dict(self.__dict__)
            tag = _dict.pop('_tag')
            children = _dict.pop('_children')
            return Element, (tag,), _dict, children

    father = Element('father')
    father.name='bill'
    child1 = Element('child1')
    child2 = Element('child2')
    father.append(child1)
    father.append(child2)

    assertEqual("Element('father',name='bill',*[Element('child1'),Element('child2')])", pyon.dumps(father))
    print(pyon.dumps(father, pretty=True))

def test_class6():
    class Author(object):
        def __init__(self, name):
            self.name = name
        def __reduce__(self):
            _dict = dict(self.__dict__)
            return Author, (), _dict
    class Article(object):
        def __init__(self, **kw):
            self.__dict__.update(kw)
        def __reduce__(self):
            return Article, (), self.__dict__

    author = Author('the author')
    lst=[Article(author=author, title='Title1'), Article(author=author, title='Title2'), Article(author=author, title='Title3')]
    assertEqual(
        "author=Author(name='the author')\n[Article(author=author,title='Title1'),Article(author=author,title='Title2'),Article(author=author,title='Title3')]",
        pyon.dumps(lst))
    print(pyon.dumps(lst, pretty=True))


def test_cross_reference_class():
    class C(object):
        def __reduce__(self):
            return C, (), self.__dict__

    lst = ['foo']
    lst.append(lst)
    d = {'a':'bar','b':lst}
    d['c'] = d
    c = C()
    c.lst = lst
    c.d = d
    c.parent = c
    d['d'] = c
    assertEqual(
        "lst=['foo',lst]\nc=C(lst=lst,d=d,parent=c)\nd={'a':'bar','c':d,'b':lst,'d':c}\n[lst,d,c]",
        pyon.dumps([lst,d,c], given={'d':d, 'lst':lst}))
    #print('1:', pyon.dumps([lst,d,c]))
    #print('2:', pyon.dumps([lst,d,c], given=pyon.currentScope()))

'''
def test_class_def1():
    class Entity(type):
        def __reduce__(cls):
            return Entity, (cls.__name__), dict(cls.__dict__)

    class Attribute(object):
        def __init__(self, type, **kwargs):
            self.type = type
            for k,v in kwargs.items():
                setattr(self, k, v)
        def __reduce__(self):
            _dict = dict(self.__dict__)
            typeName = _dict.pop('type')
            return Attribute, (typeName,), _dict

    class C(object, metaclass=Entity):
        a= Attribute(str, length=16)
        b= Attribute(int)

    print(pyon.dumps(C))
    print(pyon.dumps(C, classdef=True))
'''

def test_class_def2():
    class Entity(type):
        def __reduce__(cls):
            return Entity, (cls.__name__), dict(cls.__dict__)

    class Attribute(object):
        def __init__(self, type, **kwargs):
            self.type = type
            for k,v in kwargs.items():
                setattr(self, k, v)
        def __reduce__(self):
            _dict = dict(self.__dict__)
            typeName = _dict.pop('type')
            return Attribute, (typeName,), _dict

    class C(object):
        __metaclass__ = Entity
        a= Attribute(str, length=16)
        b= Attribute(int)

    assertEqual(
        "C",
        pyon.dumps(C))
    assertEqual(
        "Entity('C',(object,),a=Attribute(str,length=16),b=Attribute(int))",
        pyon.dumps(C, classdef=True))

def main():
    for name, func in sys.modules['__main__'].__dict__.items():
        if name.startswith('test_'):
            print('Test:', name[5:])
            func()

main()
