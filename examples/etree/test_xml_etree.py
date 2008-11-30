import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element, tostring, fromstring
from pyon import loads, dumps
import time

ETClass = Element('').__class__

def element_reduce(el):
    func = resolver(el.tag)
    if el.text is None:
        if el.tail is None:
            args = ()
        else:
            args = (None, el.tail)
    else:
        if el.tail is None:
            args = (el.text,)
        else:
            args = (el.text, el.tail)
    state = el.attrib
    items = el._children
    return func, args, state, items
ETClass.__reduce__ = element_reduce
del element_reduce
ElementTree._ElementInterface = ETClass

def Element(tag, attrib={}, **extra):
    attrib = attrib.copy()
    attrib.update(extra)
    return ETClass(tag, attrib)

cache = {}
def resolver(name):
    func = cache.get(name, None)
    if func is None:
        def func(text=None, tail=None, tag=name):
            e = Element(tag)
            if text is not None:
                e.text = text
            if tail is not None:
                e.tail = tail
            return e
        func.__name__ = name
        cache[name] = func
    return func
        
text = """
html(
  *(
    body(
      *(
        h1('Document title'),
        p('Some text', style='plain'),
        table(
          border=1,
          *(
            tr(style='rowStyle1',
              *(
                td('aaa', style='tdStyle1'), 
                td('bbb', style='tdStyle1')
              )),
            tr(style='rowStyle2',
              *(
                td('ccc', style='tdStyle2'), 
                td('ddd', style='tdStyle2')
              )),
          ))
      ))
  ))
"""
tree = loads(text, resolver)
print(tostring(tree))

s = dumps(tree)
print(s)

tree = loads(text, resolver)

s1 = dumps(tree, fast=True, pretty=True)
print(s1)

print(s == s1)

with open('hamlet.xml') as f:
    source = f.read()

t0 = time.time()
tree = fromstring(source)
t1 = time.time()
print(t1-t0)

etree_text = tostring(tree)
pyon_text = dumps(tree, fast=True)

t0 = time.time()
tree = loads(pyon_text, resolver)
t1 = time.time()
print(t1-t0)

etree_text1 = tostring(tree)

print(pyon_text[:1024])

print(etree_text1 == etree_text)
