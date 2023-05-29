from nornir import InitNornir

nr = InitNornir()

for h in nr.inventory.hosts:
    host = nr.inventory.hosts[f'{h}']
    print("-" * 30)
    print(host.hostname)
    print("-" * 30)
    print()
    print(f"Groups: {host.groups}")
    print(f"Platform: {host.platform}")
    print(f"Username: {host.username}")
    print(f"Password: {host.password}")
    print(f"Port: {host.port}")
    print()