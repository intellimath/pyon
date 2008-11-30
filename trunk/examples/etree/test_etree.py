from etree import Node, Leaf, resolverName
from pyon import loads, dumps

tree = loads(
"""
Node('author1', name='Name1', 
  *[ Node('book', title='Title11'),
     Node('book', title='Title12'),
     Leaf('memo', 'private', title='Title12'),
     Leaf('note', 'text'),
   ]
)
""")

s = dumps(tree)
print(s)

ob = loads(s, resolverName)

print(s == dumps(ob))
