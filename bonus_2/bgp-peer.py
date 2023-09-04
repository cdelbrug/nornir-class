from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir_netmiko import netmiko_send_command
from nornir_netmiko import netmiko_send_config
from nornir.core.filter import F

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


# configuring dummy prefix-list and route-map
def set_config_flags(task):
    # checking if the standard prefix-list list exists
    show_pfix_multi_result = task.run(
    task=netmiko_send_command, command_string=f"show ip prefix-list | i BMGR-")
    # extracting output from command
    pfix_output = show_pfix_multi_result[0].result

    if pfix_output:
        print("The standard BMGR- prefix-list already exists")
    else:
        print("The standard BMGR- prefix-list doesn't exist, creating dummy one")

    cfg_pfx_multi_result = task.run(
        task=netmiko_send_config,
        config_commands=[f"ip prefix-list BMGR-DUMMY-PREFIX-LIST permit 169.254.10.10/32"],
    )

    show_rm_multi_result = task.run(
    task=netmiko_send_command, command_string=f"show ip prefix-list | i BMGR-")
    rm_output = show_rm_multi_result[0].result

    if rm_output:
        print("The standard BMGR- route-map already exists")
    else:
        print("The standard BMGR- route-map doesn't exist, creating dummy one")
    
    cfg_rm_multi_result = task.run(
        task=netmiko_send_config,
        config_commands=[f"ip route-map BMGR-DUMMY-ROUTE-MAP permit 10", "match ip address prefix-list BMGR-DUMMY-PREFIX-LIST"],
    )
    

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="nxos"))
    nr.run(task=config_interfaces)
    print(nr)


if __name__ == "__main__":
    main()