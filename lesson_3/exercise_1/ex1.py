from nornir import InitNornir

nr = InitNornir()

print(f"Printing data attr of arista3: {nr.inventory.hosts['arista3'].data}")
print(f"Printing items() of arista3: {nr.inventory.hosts['arista3'].items()}")

def print_timezone(task):
    host = task.host
    print()
    print(f"Host: {host.hostname}")
    print(f"Timezone: {host.timezone}")
    print()

nr.run(task=print_timezone)

#for k,v in nr.inventory.hosts.items():
#    print(k.timezone)
#    print(v)
#    if k == 'timezone':
#        print(v)