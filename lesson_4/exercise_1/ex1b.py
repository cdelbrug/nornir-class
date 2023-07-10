import re
import colorama

from nornir import InitNornir
from nornir_netmiko import netmiko_send_command

HOUR_SECONDS = 3600
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS
TEST = True

def parse_uptime(uptime_str):
    """Based on method in the NAPALM library"""

    # import ipdb; ipdb.set_trace()
    if "uptime is" in uptime_str:
        # IOS/NX-OS
        uptime_str = uptime_str.split("uptime is")[1]
    elif "Uptime:" in uptime_str:
        # Arista
        uptime_str = uptime_str.split("Uptime: ")[1]
    else:
        # Juniper - different text form
        # System booted: 2018-10-03 20:51:06 PDT (44w1d 01:59 ago)
        # pretend it just rebooted
        return 90

    # Initialize to zero
    (years, weeks, days, hours, minutes) = (0, 0, 0, 0, 0)

    uptime_str = uptime_str.strip()
    # Replace 'and' in Arista uptime with a comma so values get split appropriately
    uptime_str = uptime_str.replace("and", ",")
    time_list = uptime_str.split(",")
    for element in time_list:
        if re.search("year", element):
            years = int(element.split()[0])
        elif re.search("week", element):
            weeks = int(element.split()[0])
        elif re.search("day", element):
            days = int(element.split()[0])
        elif re.search("hour", element):
            hours = int(element.split()[0])
        elif re.search("minute", element):
            minutes = int(element.split()[0])

    uptime_sec = (
        (years * YEAR_SECONDS)
        + (weeks * WEEK_SECONDS)
        + (days * DAY_SECONDS)
        + (hours * 3600)
        + (minutes * 60)
    )
    return uptime_sec

def uptime(task):
    # create a dict with key as platform, and value as command
    cmd_mapper = {
        "ios": "show ver | i uptime",
        "eos": "show ver | i Uptime",
        "nxos": "show ver | i uptime",
        "junos": "show system uptime | match System"
    }
    # get host object in the current task - only 1 host
    host = task.host
    # get the platform too
    platform = host.platform
    # create var cmd that contains the command for the specific platform grabbed above
    cmd = cmd_mapper[platform]
    # run the command to get the uptime
    multi_result = task.run(task=netmiko_send_command, command_string=cmd)
    # get the output
    uptime_output = multi_result[0].result
    # parse the uptime to be universal so it can be read
    uptime_sec = parse_uptime(uptime_output)
    # if uptime is less than a day
    if uptime_sec < DAY_SECONDS:
        #Make it lok nicer--yes, we are geeks
        colorama.init()
        print()
        print(colorama.Fore.RED + colorama.back.WHITE)
        print("-" * 50)
        print(f"{host.name}: device rebooted recently!")
        print(uptime_sec)
        print("-" * 50 + colorama.Style.RESET_ALL)
        print()
    # else print the uptime
    elif TEST is True:
        print()
        print("-" * 50)
        print(f"{host.name}: device uptime is: ")
        print(uptime_output)
        print("-" * 50)
        print()

def main():
    nr = InitNornir(
        config_file="config.yaml",
        runner={"plugin": "threaded", "options": {"num_workers": 10}}
    )
    nr.run(task=uptime)

if __name__ == "__main__":
    main()
