from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir.core.filter import F

nr = InitNornir(config_file="config.yaml")

ios_filt = F(groups__contains="ios")
eos_filt = F(groups__contains="eos")
nr = nr.filter(ios_filt | eos_filt)

results = nr.run(
    task=netmiko_send_command, 
    command_string="show ip arp",
    )

for key, value in results.items():
    device_output = value[0].result.split("\n")[1]
    print(f"Host: {key}, Gateway: {device_output}")