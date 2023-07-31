# this is supposed to fail

from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result

def show_ip_int_br(task):
    result = task.run(task=netmiko_send_command, command_string="show ip int br")
    if "unknown command." in result.result:
        print("Invalid command!!!@@22")


def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="srx2")
    agg_result = nr.run(task=show_ip_int_br)
    print_result(agg_result)

if __name__ == "__main__":
    main()