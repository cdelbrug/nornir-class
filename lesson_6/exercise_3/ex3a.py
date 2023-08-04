from nornir_netmiko import netmiko_send_command
from nornir import InitNornir
from nornir.core.filter import F
from getpass import getpass
from nornir_utils.plugins.functions import print_result
import logging

PASSWORD = getpass()
logger = logging.getLogger("nornir")

def mytask(task):
    task.run(task=netmiko_send_command, command_string = "show ip int br")

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="ios"))
    for hostname, host_obj in nr.inventory.hosts.items():
        host_obj.password = PASSWORD
    results = nr.run(task=mytask)
    print_result(results)
    logger.critical("CRITICAL ALERT")
    logger.error("ERROR ENTRY")
    logger.debug("DEBUG LOG ENTRY")
    

if __name__ in "__main__":
    main()