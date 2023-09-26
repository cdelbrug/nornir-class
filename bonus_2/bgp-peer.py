from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir_netmiko import netmiko_send_command
from nornir_netmiko import netmiko_send_config
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.filter import F
from ciscoconfparse import CiscoConfParse
from pprint import pprint

# the configuration that should be pushed as an example
'''
# Use ASN=22 for both nxos1 and nxos2
router bgp 22
  router-id 172.31.101.101
  address-family ipv4 unicast
    # Networks to potentially advertise
    network 172.31.101.101/32
    network 172.31.102.101/32
  # Remote BGP Peers
  neighbor 172.31.254.2
    remote-as 22
    description configured by nornir
    address-family ipv4 unicast
      # Bind to a route-map
      route-map RM_BGP_NXOS2_Peer out

# Route-map entries (should reference a prefix-list)
route-map RM_BGP_NXOS2_Peer permit 100
  match ip address prefix-list PL_BGP_Loopback101 

# Prefix-list entries
ip prefix-list PL_BGP_Loopback101 seq 5 permit 172.31.101.101/32
'''

def config_interfaces(task):
    # feed in the data variables in the inventory file from the task.host var (current host in task)
    intf_multi_result = task.run(task=template_file, template="intf.j2", path=".", **task.host)
    # extract config rendered
    intf_rendered_config = intf_multi_result[0].result
    task.host["intf_config"] = intf_rendered_config
    print(task.host["intf_config"])
    intf_result = task.run(task=napalm_configure, configuration=intf_rendered_config)
    print(intf_result)

# configuring dummy prefix-list and route-map
def set_config_flags(task):
    # checking if the standard prefix-list list exists
    show_pfix_multi_result = task.run(
    task=netmiko_send_command, command_string=f"show ip prefix-list | i BMGR-")
    # extracting output from command
    pfix_output = show_pfix_multi_result[0].result
    # idempotent check and config of dummy prefix-list
    if pfix_output:
        print("The standard BMGR- prefix-list already exists")
    else:
        print("The standard BMGR- prefix-list doesn't exist, creating dummy one")
        cfg_pfx_multi_result = task.run(
            task=netmiko_send_config,
            config_commands=[f"ip prefix-list BMGR-DUMMY-PREFIX-LIST permit 169.254.10.10/32"],
        )
    # idempotent check and config of dummy prefix-list
    show_rm_multi_result = task.run(
    task=netmiko_send_command, command_string=f"show run | i BMGR-DUMMY-ROUTE-MAP")
    rm_output = show_rm_multi_result[0].result
    
    if rm_output:
        print("The standard BMGR- route-map already exists")
    else:
        print("The standard BMGR- route-map doesn't exist, creating dummy one")
        cfg_rm_multi_result = task.run(
            task=netmiko_send_config,
            config_commands=[f"route-map BMGR-DUMMY-ROUTE-MAP permit 10", "match ip address prefix-list BMGR-DUMMY-PREFIX-LIST"],
        )
    # baseline bgp config, napalm merge is idempotent? merge is default
    bgp_result = task.run(task=napalm_configure, configuration='feature bgp\nrouter bgp 22')
    
def get_checkpoint(task):
    backup_output = task.host.connections["napalm"].connection._get_checkpoint_file()
    task.host["backup_config"] = backup_output
    print(task.host["backup_config"])

def render_configs(task):
    prefix_conf_multi_result = task.run(task=template_file, template="prefix-list.j2", path=".", **task.host)
    prefix_rendered_config = prefix_conf_multi_result[0].result
    rm_conf_multi_result = task.run(task=template_file, template="route-map.j2", path=".", **task.host)
    rm_rendered_config = rm_conf_multi_result[0].result
    bgp_conf_multi_result = task.run(task=template_file, template="bgp.j2", path=".", **task.host)
    bgp_rendered_config = bgp_conf_multi_result[0].result
    print(prefix_rendered_config)
    print(rm_rendered_config)
    print(bgp_rendered_config)
    task.host["prefix_list_config"] = prefix_rendered_config
    task.host["rm_config"] = rm_rendered_config
    task.host["bgp_config"] = bgp_rendered_config

def merge_configs(task):
    # converting config to list as required by confparse, then parsing it
    parse = CiscoConfParse(task.host["backup_config"].splitlines())
    # finding where the placeholder prefix=list is and storing as obj
    matching_prefix_lines = parse.find_objects(r"ip prefix-list BMGR-DUMMY-PREFIX-LIST")
    matching_route_maps = parse.find_objects(r"route-map BMGR-DUMMY-ROUTE-MAP")
    # iterating over matching prefix obj for all lines that match
    for matching_line in matching_prefix_lines:
        # converting generated config to list because the parsed config is a list
        #
        for line in task.host["prefix_list_config"].splitlines():
            # inserting my generated config after the dummy placeholder pfxlist
            matching_line.insert_after(line)
    for matching_line2 in matching_route_maps:
        for line in task.host["rm_config"].splitlines():
            # trying insert_before so I don't have to mess with route-map
            # child entries
            matching_line2.insert_before(line)
    # it's added here so i'm printing it.
    print(parse.ioscfg)
    # starting the bgp merge with the existing config in-tact
    # using sync_diff with remove_lines=False
    

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="nxos"))
    #nr.run(task=config_interfaces)
    print(nr)
    nr.run(task=set_config_flags)
    nr.run(task=get_checkpoint)
    nr.run(task=render_configs)
    nr.run(task=merge_configs)
    print()


if __name__ == "__main__":
    main()