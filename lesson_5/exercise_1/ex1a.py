from nornir import InitNornir
from nornir_netmiko import netmiko_send_config
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result

def mytask(task):
    snmp_id = task.host["snmp_id"]
    if task.host.platform == "ios":
        cfg = f"snmp-server chassis-id {snmp_id}"
    else:
        cfg = f"snmp chassis-id {snmp_id}-{task.host.name}"
    task.run(netmiko_send_config, config_commands=cfg)

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="ios") | F(groups__contains="eos"))
    results = nr.run(task=mytask)
    print_result(results)

if "__main__" == __name__:
    main()