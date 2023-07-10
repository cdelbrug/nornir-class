from nornir import InitNornir
from nornir_netmiko import netmiko_send_command

def uptime(task):
    cmd_mapper = {
        "ios": "show ver | i uptime",
        "eos": "show ver | i Uptime",
        "nxos": "show ver | i uptime",
        "junos": "show system uptime | match System"
    }
    host = task.host
    platform = host.platform
    cmd = cmd_mapper[platform]
    task.run(task=netmiko_send_command, command_string=cmd)

def main():
    nr = InitNornir(config_file="config.yaml")
    aggr_result = nr.run(task=uptime)
    for hostname, multi_result in aggr_result.items():
        print()
        print("-" * 50)
        # not sure why 0 is uptime task with no info in it
        # and why I have to reference 1 in the index
        print(f"{hostname}: {multi_result[1].result}")
        print("-" * 50)
        print()

if __name__ == "__main__":
    main()
