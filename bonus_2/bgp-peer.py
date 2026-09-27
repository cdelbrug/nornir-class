import argparse
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
    task=netmiko_send_command, command_string=f"show ip prefix-list | i BMGR-DUMMY-PREFIX-LIST")
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

def managed_lines(parse, linespec):
    # line numbers of every block matching linespec, parent and children
    line_nums = set()
    for obj in parse.find_objects(linespec):
        line_nums.add(obj.linenum)
        line_nums.update(child.linenum for child in obj.all_children)
    return line_nums

def build_candidate_config(backup_config, prefix_config, rm_config, bgp_config):
    parse = CiscoConfParse(backup_config.splitlines(), ignore_blank_lines=False)
    # drop blank lines from the rendered templates
    new_prefix = [line for line in prefix_config.splitlines() if line.strip()]
    new_rm = [line for line in rm_config.splitlines() if line.strip()]
    new_bgp = [line for line in bgp_config.splitlines() if line.strip()]

    # everything BMGR- owns gets removed, except the dummy placeholders
    # which stay in as anchors for where the new config goes
    skip = set()
    skip |= managed_lines(parse, r"^ip prefix-list BMGR-(?!DUMMY-)")
    skip |= managed_lines(parse, r"^route-map BMGR-(?!DUMMY-)")
    skip |= managed_lines(parse, r"^router bgp\s")

    # line number -> config to put before/after that line
    insert_before = {}
    insert_after = {}

    # prefix-lists go right after the dummy prefix-list
    pfx_anchor = parse.find_objects(r"^ip prefix-list BMGR-DUMMY-PREFIX-LIST")[-1]
    insert_after[pfx_anchor.linenum] = new_prefix

    # route-maps go right before the dummy route-map so I don't
    # have to mess with the dummy's child entries
    rm_anchor = parse.find_objects(r"^route-map BMGR-DUMMY-ROUTE-MAP")[0]
    insert_before[rm_anchor.linenum] = new_rm

    # the whole router bgp block gets swapped for the rendered one, in the
    # same spot. set_config_flags makes sure a router bgp block exists
    bgp_anchor = parse.find_objects(r"^router bgp\s")[0]
    insert_before[bgp_anchor.linenum] = new_bgp

    # rebuild the config one line at a time; building a new list keeps
    # the inserted lines in order (insert_after on the same line flips them)
    candidate = []
    for obj in parse.ConfigObjs:
        candidate.extend(insert_before.get(obj.linenum, []))
        if obj.linenum not in skip:
            candidate.append(obj.text)
        candidate.extend(insert_after.get(obj.linenum, []))
    return "\n".join(candidate) + "\n"

def merge_configs(task):
    task.host["candidate_config"] = build_candidate_config(
        task.host["backup_config"],
        task.host["prefix_list_config"],
        task.host["rm_config"],
        task.host["bgp_config"],
    )
    print(task.host["candidate_config"])

def push_config(task, dry_run=True):
    # full config replace off the checkpoint, so BGP peers/prefix-lists/
    # route-maps that aren't in the inventory anymore get removed
    push_result = task.run(
        task=napalm_configure,
        configuration=task.host["candidate_config"],
        replace=True,
        dry_run=dry_run,
    )
    diff = push_result[0].diff
    print(f"----- {task.host.name} {'(dry run) ' if dry_run else ''}-----")
    print(diff if diff else "No changes")

def main():
    parser = argparse.ArgumentParser(description="BGP peer manager")
    parser.add_argument("--commit", action="store_true",
                        help="push the changes (default is a dry run that only shows the diff)")
    args = parser.parse_args()

    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="nxos"))
    #nr.run(task=config_interfaces)
    print(nr)
    nr.run(task=set_config_flags)
    nr.run(task=get_checkpoint)
    nr.run(task=render_configs)
    nr.run(task=merge_configs)
    nr.run(task=push_config, dry_run=not args.commit)
    print()


if __name__ == "__main__":
    main()
