from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import random
# to catch exceptions in subtasks
from nornir.core.exceptions import NornirSubTaskError
# to catch authentication error exceptions
from netmiko import NetMikoAuthenticationException
import os

def getclock(task):
    if task.host.platform == "junos":
        command = "show system uptime"
    else:
        command = "show clock"
    try:
        task.run(netmiko_send_command, command_string=command)
    except NornirSubTaskError as e:
        # finding a specific exception within NornirSubtaskError 
        # if authentication failed
        if isinstance(e.result.exception, NetMikoAuthenticationException):
            # removing failed task so print_result is cleaner and only shows success
            # will still show in the nornir.log file tho if you wanna check...
            task.results.pop()
            # setting password to the correct vlaue now
            task.host.password = os.environ["NORNIR_PASSWORD"]
            # try subtask again
            task.run(netmiko_send_command, command_string=command)
        else:
            return "I dont know what happened..."


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