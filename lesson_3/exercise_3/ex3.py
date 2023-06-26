from nornir import InitNornir
from nornir.core.filter import F


#ex3a
print("ex3a")
nr = InitNornir()
nr = nr.filter(F(role="AGG"))
print(nr.inventory.hosts)
print()

#ex3b
print("ex3b")
nr = InitNornir()
nr = nr.filter(F(groups__contains="sea") | F(groups__contains="sfo"))
print(nr.inventory.hosts)
print()

#ex3c
print("ex3c")
nr = InitNornir()
nr = nr.filter(F(role="WAN") & F(site_details__wifi_password__contains="racecar"))
print(nr.inventory.hosts)
print()

#ex3d
print("ex3d")
nr = InitNornir()
nr = nr.filter(F(role="WAN") & ~F(site_details__wifi_password__contains="racecar"))
print(nr.inventory.hosts)
print()


