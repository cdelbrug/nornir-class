from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
import os

nr = InitNornir(config_file="config.yaml")

ios_filt = F(groups__contains="ios")
nr = nr.filter(ios_filt)
nr.inventory.hosts["cisco3"].password = 'bogus'

results = nr.run(
    task=netmiko_send_command, 
    command_string="show ip int brief",
    )

print_result(results)
print()
print("=" * 50)
print("Printing results.failed_hosts")
print("=" * 50)
print()
print(results.failed_hosts)
print()
print("=" * 50)
print("Printing more details")
print("=" * 50)
print()
for k,v in results.failed_hosts.items():
    print("-" * 50)
    print("Hostname")
    print("-" * 50)
    print()
    print(k)
    print()
    print("-" * 50)
    print("Result")
    print("-" * 50)
    print()
    print(v[0].result)
print("=" * 50)
print("Printing nr.data.failed_hosts")
print("=" * 50)
print()
print("-" * 50)
print(nr.data.failed_hosts)
print("-" * 50)
print()

#5c
#nr.inventory.hosts["cisco3"].password = os.environ["NORNIR_PASSWORD"]
#
#results_again = nr.run(
#    task=netmiko_send_command, 
#    command_string="show ip int brief",
#    on_good=False,
#    on_failed=True
#    )
#
#print_result(results_again)

#5d
print()
print("=" * 50)
print("Printing results.failed_hosts")
print("=" * 50)
print()
print(nr.data.failed_hosts)
print()
print("Clearing failed host cisco3...")
nr.data.recover_host("cisco3")
print("Done")
print()
print("=" * 50)
print("Printing results.failed_hosts")
print("=" * 50)
print()
print(nr.data.failed_hosts)
print()