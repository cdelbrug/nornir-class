from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from pprint import pprint

nr = InitNornir(config_file="config.yaml")

nr = nr.filter(F(groups__contains="eos"))

results = nr.run(task=netmiko_send_command,
       command_string="show interface status",
       use_textfsm=True)

print_result(results)

final_dict = {}

for device_name, multi_result in results.items():
    # adding the device name as a dictionary then
    # creating a dict inside of it
    final_dict[device_name] = {}
    device_result = multi_result[0]
    # going through list of dictionaries
    # which are interfaces
    for intf_dict in device_result.result:
        intf_name = intf_dict["port"]
        inner_dict = {}
        inner_dict["status"] = intf_dict["status"]
        inner_dict["vlan"] = intf_dict["vlan"]
        # adding intf_name dictionary key, and adding
        # another dictionary inside intf_name that 
        # was put together above
        final_dict[device_name][intf_name] = inner_dict
pprint(final_dict)