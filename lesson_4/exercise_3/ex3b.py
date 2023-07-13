from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command
from nornir_netmiko import netmiko_send_config

# create task that accepts vlan id and name
def configure_vlans(task, vlan_id, vlan_name):
    
    multi_result = task.run(
        task=netmiko_send_command, command_string=f"show vlan brief | i {vlan_id}"
    )

    vlan_out = multi_result[0].result
    # we specifically looked for our vlan ID so if the 
    # result is empty / False then proceed to run the task
    # to add it!
    if vlan_out:
        # create list based on spaces (there should be 3)
        # grab the vlan id from the first in the list
        existing_vlan_id = vlan_out.split()[0]
        # then grab the name
        existing_vlan_name = vlan_out.split()[1]
        # then compare with the variables
        if existing_vlan_id == vlan_id and existing_vlan_name == vlan_name:
            return "No changes: config already correct."
    
    task.run(
        task=netmiko_send_config,
        config_commands=[f"vlan {vlan_id}", f"name {vlan_name}"],
    )
    return "Config changed."

def main():
    # I guess you use capital letters for variables in tasks/functions?
    VLAN_ID = "555"
    VLAN_NAME = "jacks_vlan"

    nr = InitNornir(config_file="config.yaml")
    # grab devices in group eos OR nxos
    nr = nr.filter(F(groups__contains="eos") | F(groups__contains="nxos"))
    # configure vlans, providing vlan id and name
    result = nr.run(task=configure_vlans, vlan_id=VLAN_ID, vlan_name=VLAN_NAME)

    print_result(result)

if __name__ == "__main__":
    main()