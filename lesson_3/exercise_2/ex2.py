from nornir import InitNornir
from nornir.core.filter import F


#ex2a
print("ex2a")
nr = InitNornir()
nr = nr.filter(name="arista1")
print(nr.inventory.hosts)
print()

#ex2b
print("ex2b")
nr = InitNornir()
nr = nr.filter(role="WAN")
print(nr.inventory.hosts)
print()

#ex2bb
print("ex2bb")
nr = InitNornir()
nr = nr.filter(role="WAN")
nr = nr.filter(port=22)
print(nr.inventory.hosts)
print()

#ex2c
print("ex2c")
nr = InitNornir()
nr = nr.filter(F(groups__contains="sfo"))
print(nr.inventory.hosts)
print()


