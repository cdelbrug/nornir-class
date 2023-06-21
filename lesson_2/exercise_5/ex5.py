from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")

ios_filt = F(groups__contains="ios")
nr = nr.filter(ios_filt)
nr.inventory.hosts["cisco3"].password = 'bogus'

results = nr.run(
    task=netmiko_send_command, 
    command_string="show ip int brief",
    )

print_result(results)
print("-" * 50)
print("Printing results.failed_hosts")
print("-" * 50)
print()
print(results.failed_hosts)
for host in results.failed_hosts:
    print(host[0].result)
print("Printing failed hostnames")
print("-" * 50)
print()
print(nr.data.failed_hosts)