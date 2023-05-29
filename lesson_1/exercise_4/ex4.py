from nornir import InitNornir

nr = InitNornir()

def mytask(task):
    print("-" * 30)
    print(task.host.hostname)
    print("-" * 30)
    print()
    print("Hey there")
    print()

nr.run(task=mytask)