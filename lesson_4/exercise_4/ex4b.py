#import napalm.eos
#import napalm.nxos

from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_configure


def configure_vlan(task, vlan_id, vlan_name, dry_run=True):
    # adds multi lines to create a line break I think
    config_string = f'''vlan {vlan_id}
    name {vlan_name}'''
    # napalm configure allows a dry_run thing to be set
    task.run(task=napalm_configure, configuration=config_string, dry_run=dry_run)


def main():

    VLAN_ID = "555"
    VLAN_NAME = "jacks-vlan"
    DRY_RUN = True

    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="eos") | F(groups__contains="nxos"))
    result = nr.run(task=configure_vlan, vlan_id=VLAN_ID, vlan_name=VLAN_NAME, dry_run=DRY_RUN)
    # the results show the same thing if its dry_run or not. 
    # so not sure how you can tell it was a dry run unless you 
    # check the device config
    print_result(result)

if __name__ == "__main__":
    main()
