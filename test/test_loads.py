#
import pyon
import ast
import sys

def assertEqual(expected, result):
    if expected != result:
        print('*** Expected: ', expected, ' Result: ', result)

def test_int():
    assertEqual(17, pyon.loads('17'))

def test_float():
    assertEqual(3.14, pyon.loads('3.14'))

def test_bool():
    assertEqual(True, pyon.loads('True'))
    assertEqual(False, pyon.loads('False'))

def test_long():
    assertEqual(1000000000000000, pyon.loads('1000000000000000'))

def test_string():
    assertEqual('abs', pyon.loads("'abs'"))

def test_bytes():
    assertEqual(b'abs', pyon.loads("b'abs'"))

def test_list():
    assertEqual([1, 'abc', True], pyon.loads("[1, 'abc', True]"))
    assertEqual([], pyon.loads("[]"))
    assertEqual([2], pyon.loads("[2]"))

def test_tuple():
    assertEqual((1, 'abc', True), pyon.loads("(1, 'abc', True)"))
    assertEqual((1,), pyon.loads("(1,)"))
    assertEqual((), pyon.loads("()"))

def test_dict():
    assertEqual({'a':1, 'abc':3.14, (1,2):True}, pyon.loads("{'a':1, 'abc':3.14, (1,2):True}"))
    assertEqual({}, pyon.loads("{}"))
    assertEqual({'a':1}, pyon.loads("{'a':1}"))

def test_set():
    assertEqual({True,2,'abc',(1,2,3)}, pyon.loads("{True,2,'abc',(1,2,3)}"))
    assertEqual(set(), pyon.loads("set()"))

def test_frozenset():
    assertEqual(frozenset({True,2,'abc',(1,2,3)}), pyon.loads("frozenset({True,2,'abc',(1,2,3)})"))
    assertEqual(frozenset(), pyon.loads("frozenset()"))

def test_class1():
    class C(object):
        pass

    c = pyon.loads('C()')
    assertEqual(type(c), C)
    assertEqual(len(c.__dict__), 0)

def test_class2():
    class C(object):
        pass

    c = pyon.loads('C(a=1,b="python",c=[1,2])')
    assertEqual(type(c), C)
    assertEqual(len(c.__dict__), 3)
    assertEqual(c.a, 1)
    assertEqual(c.b, "python")
    assertEqual(c.c, [1,2])

def test_class3():
    class C(list):
        pass

    c = pyon.loads('C(a=1,b=2, *["a","b","c"])')
    assertEqual(type(c), C)
    assertEqual(len(c.__dict__), 2)
    assertEqual(c.a, 1)
    assertEqual(c.b, 2)
    assertEqual(c[0], 'a')
    assertEqual(c[1], 'b')
    assertEqual(c[2], 'c')

def test_class4():
    class Element(object):
        def __new__(cls, tag):
            inst = super(Element, cls).__new__(cls)
            inst._tag = tag
            inst._children = []
            return inst
        def __init__(self, tag):
            self._tag = tag
            self._children = []
        def __setstate__(self, state):
            self.__dict__.update(state)
        def append(self, e):
            self._children.append(e)

    c = pyon.loads('Element("father", name="bill", *[Element("child1"), Element("child2")])')
    assertEqual(c._tag, "father")
    assertEqual(c.name, "bill")
    assertEqual(c._children[0]._tag, "child1")
    assertEqual(c._children[1]._tag, "child2")

def test_class5():
    class Element(object):
        def __new__(cls, tag):
            inst = super(Element,cls).__new__(cls)
            inst._tag = tag
            inst._children = []
            inst._options = {}
            return inst
        def __setstate__(self, state):
            self.__dict__.update(state)
        def append(self, e):
            self._children.append(e)
        def __setitem__(self, key, item):
            self._options[key] = item

    c = pyon.loads('Element("father", name="bill", *[Element("child1"), Element("child2")], **{"gen":1, "out":"stdout"})')
    assertEqual(c._tag, "father")
    assertEqual(c.name, "bill")
    assertEqual(c._children[0]._tag, "child1")
    assertEqual(c._children[1]._tag, "child2")
    assertEqual(c._options, {"gen":1, "out":"stdout"})

def test_class6():
    class Author(object):
        def __init__(self, name):
            self.name = name
    class Article(object):
        pass

    c = pyon.loads(
"""
author = Author('the author')
[Article(author=author, title='Title1'), Article(author=author, title='Title2'), Article(author=author, title='Title3')]
""")
    assertEqual(c[0].author, c[1].author)
    assertEqual(c[1].author, c[2].author)
    assertEqual(c[0].title, 'Title1')
    assertEqual(c[1].title, 'Title2')
    assertEqual(c[2].title, 'Title3')

"""
def test_class7():
    class C(object):
       def __init__(self, a, b, c=5, *args, d, e='abc', **kwargs):
           self.a = a
           self.b = b
           self.c = c
           self.args = args
           self.d = d
           self.e = e
           self.kwargs = kwargs
           
    c = pyon.loads("C(1, 2, d='a')")
    assertEqual(c.a, 1)
    assertEqual(c.b, 2)
    assertEqual(c.c, 5)
    assertEqual(c.args, ())
    assertEqual(c.d, 'a')
    assertEqual(c.e, 'abc')
    assertEqual(c.kwargs, {})

def test_class8():
    class C(object):
       def __init__(self, a, b, c=5, *args, d, e='abc', **kwargs):
           self.a = a
           self.b = b
           self.c = c
           self.args = args
           self.d = d
           self.e = e
           self.kwargs = kwargs
           
    c = pyon.loads("C(1, 2, 3, 4, 5, 6, d='a', e='b', f='d', h='e')")
    assertEqual(c.a, 1)
    assertEqual(c.b, 2)
    assertEqual(c.c, 3)
    assertEqual(c.args, (4, 5, 6))
    assertEqual(c.d, 'a')
    assertEqual(c.e, 'b')
    assertEqual(c.kwargs, {'f':'d', 'h':'e'})
"""

def test_recursive_list():
    lst = pyon.loads(
"""
lst = ['foo', lst]
lst
""")
    assert lst is lst[1]

def test_recursive_dict():
    d = pyon.loads(
"""
d = {'a':'foo', 'b':d}
d
""")
    assert d is d['b']

def test_cross_reference():
    ob = pyon.loads(
"""
lst = ['foo', lst, d]
d = {'a':'foo', 'b':d, 'c':lst}
[d, lst]
""")
    lst = ob[1]
    d = ob[0]
    assert lst[1] is lst
    assert d is d['b']
    assert lst[2] is d
    assert d['c'] is lst

def test_recursive_class():
    class C(object):
        pass

    c = pyon.loads('c=C(parent=c)\nc')
    assert c.parent is c

def test_cross_reference_class():
    class C(object):
        pass

    ob = pyon.loads(
"""
c = C(parent=c, lst=lst, d=d)
lst = ['foo', lst, d, c]
d = {'a':'foo', 'b':d, 'c':lst, 'd':c}
[d, lst, c]
""")
    lst = ob[1]
    d = ob[0]
    c = ob[2]
    assert c.parent is c
    assert c.lst is lst
    assert c.d is d
    assert d is d['b']
    assert lst[2] is d
    assert d['c'] is lst
    assert d['d'] is c
    assert lst[3] is c

def main():
    for name, func in sys.modules['__main__'].__dict__.items():
        if name.startswith('test_'):
            print('Test:', name[5:])
            func()

main()
