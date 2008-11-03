#
import pyon
import ast
import sys

def assertEqual(expected, result):
    if expected != result:
        print('*** Expected: ', expected, ' Result: ', result)

def test_int():
    assertEqual('17', pyon.dumps(17))

#def test_float():
#    assertEqual(3.14, pyon.dums(3.14))

def test_bool():
    assertEqual('True', pyon.dumps(True))
    assertEqual('False', pyon.dumps(False))

def test_long():
    assertEqual('1000000000000000', pyon.dumps(1000000000000000))

def test_string():
    assertEqual("'abs'", pyon.dumps('abs'))

def test_list():
    assertEqual("[1,'abc',True]", pyon.dumps([1, 'abc', True]))

def test_tuple():
    assertEqual("(1,'abc',True)", pyon.dumps((1, 'abc', True)))

def test_dict():
    assertEqual("{'a':1,(1,2):True,'abc':3}", pyon.dumps({'a': 1, 'abc': 3, (1, 2): True}))

def test_with_assigns1():
    p1 = (1,2)
    p2 = [1,2]    
    assertEqual("_p__0=(1,2)\n_p__1=[1,2]\n[_p__0,_p__1,_p__0,_p__1]", pyon.dumps([p1,p2,p1,p2], fast=False))
    assertEqual("[(1,2),[1,2],(1,2),[1,2]]", pyon.dumps([p1,p2,p1,p2]))

def test_with_assigns1_1():
    p1 = (1,2)
    p2 = [1,2]    
    assertEqual("[(1,2),[1,2]]", pyon.dumps([p1,p2], fast=False))
    assertEqual("[(1,2),[1,2],(1,2),[1,2]]", pyon.dumps([p1,p2,p1,p2]))
    
def test_with_assigns2():
    lst = ['foo']
    lst.append(lst)
    print(pyon.dumps(lst, fast=False))
 
def test_with_assigns3():
    p1 = (1,2)
    p2 = [1,2]    
    assertEqual("_p__0=(1,2)\n_p__1=[1,2]\n{'a':_p__0,'c':_p__0,'b':_p__1,'d':_p__1}", pyon.dumps({'a':p1,'b':p2,'c':p1,'d':p2}, fast=False))

def test_with_assigns4():
    d = {'a':'foo'}
    d['b'] = d
    print(pyon.dumps(d, fast=False))
    
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
    assertEqual("_p__0=C()\n_p__0.parent=_p__0\n_p__0", pyon.dumps(c, fast=False))


def test_class2():
    class C(object):
        def __reduce__(self):
            return C, (), self.__dict__

    c = C()
    c.a = 1
    c.b = 'python'
    c.c = [1,2]
    assertEqual("C(a=1,c=[1,2],b='python')", pyon.dumps(c))


def test_class3():
    class C(list):
        def __reduce__(self):
            return C, (), self.__dict__, list(self)

    c = C()
    c.a = 1
    c.b = 2
    c.extend(['a','b','c'])
    assertEqual("C(a=1,b=2,*['a','b','c'])", pyon.dumps(c))


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

def test_class6():
    class Author(object):
        def __init__(self, name):
            self.name = name
        def __reduce__(self):
            _dict = dict(self.__dict__)
            name = _dict.pop('name')
            return Author, (name,), _dict
    class Article(object):
        def __init__(self, **kw):
            self.__dict__.update(kw)
        def __reduce__(self):
            return Article, (), self.__dict__

    author = Author('the author')
    lst=[Article(author=author, title='Title1'), Article(author=author, title='Title2'), Article(author=author, title='Title3')]
    print(pyon.dumps(lst, fast=False))
        
    
def main():
    for name, func in sys.modules['__main__'].__dict__.items():
        if name.startswith('test_'):
            print('Test:', name[5:])
            func()

main()
