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

def test_list():
    assertEqual([1, 'abc', True], pyon.loads("[1, 'abc', True]"))

def test_tuple():
    assertEqual((1, 'abc', True), pyon.loads("(1, 'abc', True)"))

def test_dict():
    assertEqual({'a':1, 'abc':3.14, (1,2):True}, pyon.loads("{'a':1, 'abc':3.14, (1,2):True}"))

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
        def __init__(self, tag):
            self._tag = tag
            self._children = []
            self._options = {}
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
    
def main():
    for name, func in sys.modules['__main__'].__dict__.items():
        if name.startswith('test_'):
            print('Test:', name[5:])
            func()

main()
