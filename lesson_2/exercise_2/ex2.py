from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command

#2a
filter=F(groups__contains="ios")
nr = InitNornir(config_file="config.yaml")
nr = nr.filter(filter)
print(f"IOS Hosts: {nr.inventory.hosts}")

#2b
my_results = nr.run(task=netmiko_send_command, command_string="show run | i hostname")

print(f"Inspect my_results keys: {type(my_results.keys())}")
print(f"Inspect my_results items: {type(my_results.items())}")
print(f"Inspect my_results values: {type(my_results.values())}")

print(f"Print my_results keys: {my_results.keys()}")
print(f"Print my_results items: {my_results.items()}")
print(f"Print my_results values: {my_results.values()}")

#2c
host_results = my_results["cisco3"]
print(f"Inspecting host_result: {type(host_results)}")
print(f"Printing first entry in hosts_result: {host_results[0]}")

# checking if iterable object or not
print("Checking if host_results is iterable")
for i in host_results:
    print(i)

#2d
print()
print("Printing first host_result info:")
print()
task_result = host_results[0]
print(type(task_result))
print(task_result.host)
print(task_result.name)
print(task_result.result)
print("^^^ That is the actual result")
print(task_result.failed)
print()

#2e
# my_results is the result of the task running on all hosts.
# it has a dict like structure which is broken up by host
# more info is in the host object

# host_results is the result for one of the hosts in the my_results aggresult.
# it contains info on the task that was run on that individual host

# task_result is the single host's result object that has the result, name of the host, command that was ran, etc
