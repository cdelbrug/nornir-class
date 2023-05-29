from nornir import InitNornir

nr = InitNornir()

def mytask(task):
    print("-" * 30)
    print(task.host.hostname)
    print("-" * 30)
    print()
    print(f"DNS1: {task.host['dns1']}")
    print(f"DNS2: {task.host['dns2']}")
    print()
    print("Banner MOTD: Hey there")
    print()

nr.run(task=mytask)