#import napalm.eos
#import napalm.nxos

from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_configure


def configure_vlan(task, vlan_id, vlan_name):
    config_string = f'''vlan {vlan_id}
    name {vlan_name}'''
    task.run(task=napalm_configure, configuration=config_string)


def main():

    VLAN_ID = "555"
    VLAN_NAME = "jacks-vlan"

    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="eos") | F(groups__contains="nxos"))
    result = nr.run(task=configure_vlan, vlan_id=VLAN_ID, vlan_name=VLAN_NAME)
    print_result(result)

if __name__ == "__main__":
    main()
