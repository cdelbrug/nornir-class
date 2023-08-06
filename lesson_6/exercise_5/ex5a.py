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
    task.run(netmiko_send_command, command_string=command)

def main():
    nr = InitNornir(config_file="config.yaml")
    results = nr.run(task=getclock)
    print_result(results)

if "__main__" == __name__:
    main()