import pyon
import pickle
import time
import ast
import json

class C(object):
   def __init__(self, count):
      self.count = count
   #
   def __reduce__(self):
      _dict = {'name':self.name, 'age':self.age}
      try:
          _dict['child'] = self.child
      except:
           pass
      return C, (self.count,), _dict

lst = []
for i in range(10000):
   c = C(i)
   c.name = "aaa" + str(i)
   c.age = 100*i % 37
   c.child = C(i)
   c.child.name = "bbb" + str(i)
   c.child.age = 101*i % 37
   lst.append(c)

json_lst = []
for i in range(10000):
   c= {'name':"aaa" + str(i), 'count':i, 'age': 100*i % 37, 'child': {'name':"bbb" + str(i), 'count':i, 'age':101*i % 37}}
   json_lst.append(c)

print("--- PyON ---")

t0 = time.time()
text = pyon.dumps(lst, fast=True)
t1 = time.time()
#print('Text length = ', len(text))
print('pyon dumps:', t1-t0)
t2 = time.time()
obj = pyon.loads(text)
t3 = time.time()
print('pyon loads:', t3-t2)
tree = ast.parse(text)
t2 = time.time()
obj = pyon.loads(tree)
t3 = time.time()
print('pyon loads without ast part:', t3-t2)
#print('List length = ',len(obj))

print("--- pickle ---")

t0 = time.time()
text = pickle.dumps(lst)
t1 = time.time()
#print('Text length = ', len(text))
print('pickle dumps:', t1-t0)
t2 = time.time()
obj = pickle.loads(text)
t3 = time.time()
print('pickle loads:', t3-t2)
#print('List length = ',len(obj))

print("--- json ---")

t0 = time.time()
text = json.dumps(json_lst)
t1 = time.time()
print('json dumps:', t1-t0)
t0 = time.time()
ob = json.loads(text)
t1 = time.time()
print('json loads:', t1-t0)
t0 = time.time()
text = pyon.dumps(json_lst, fast=True)
t1 = time.time()
print('pyon dumps:', t1-t0)
t0 = time.time()
ob = pyon.loads(text)
t1 = time.time()
print('pyon loads:', t1-t0)
tree = ast.parse(text)
t0 = time.time()
ob = pyon.loads(tree)
t1 = time.time()
print('pyon loads without ast part:', t1-t0)