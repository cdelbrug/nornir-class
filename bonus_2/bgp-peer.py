from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir_netmiko import netmiko_send_config
from nornir.core.filter import F

def config_interfaces(task):
    # feed in the data variables in the inventory file from the task.host var (current host in task)
    intf_multi_result = task.run(task=template_file, template="intf.j2", path=".", **task.host)
    # extract config rendered
    int_rendered_config = intf_multi_result[0].result
    print()

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="nxos"))
    nr.run(task=config_interfaces)
    print(nr)


if __name__ == "__main__":
    main()