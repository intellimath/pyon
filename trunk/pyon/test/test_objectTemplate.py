#

from pyon import loads

class A(object):
    pass
    
class A1(object):
   pass
   
class A2(object):
   pass
   
ob =  loads("""
A(x=1, 
  y=IF(
    flag, 
    A1(kind='A1'), 
    A2(kind='A2')
  )
)
""", flag=True)
print(True, type(ob.y), ob.y.kind)
ob =  loads("A(x=1, y=IF(flag, A1(kind='A1'), A2(kind='A2')))", flag=False)
print(False, type(ob.y), ob.y.kind)
