from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import random
from nornir.core.exceptions import NornirSubTaskError

def getclock(task):
    if task.host.platform == "junos":
        command = "show system uptime"
    else:
        command = "show clock"
    try:
        task.run(netmiko_send_command, command_string=command)
    except NornirSubTaskError as e:
        print(e)

def changepw(task, nrobj):
    for host, data in nrobj.inventory.hosts.items():
        if random.choice([True, False]):
            data.password = "asdklfjlksdjf"

def main():
    nr = InitNornir(config_file="config.yaml")
    nr.run(task=changepw, nrobj=nr)
    results = nr.run(task=getclock)
    print_result(results)

if "__main__" == __name__:
    main()