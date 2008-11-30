from etree import Element, Item, resolverName
from pyon import loads, dumps

tree = loads(
"""
Element('author1', name='Name1', 
  *[ Element('book', title='Title11'),
     Element('book', title='Title12'),
     Item('memo', 'private', title='Title12'),
     Item('note', 'text'),
   ]
)
""")

s = dumps(tree)
print(s)

ob = loads(s, resolverName)

print(s == dumps(ob))
