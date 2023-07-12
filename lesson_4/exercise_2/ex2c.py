from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_file_transfer
from nornir_netmiko import netmiko_send_command

def file_copy(task):
    # set the current host obj as var
    host = task.host
    # record current host obj platform in var
    platform = host.platform
    # obtain the file name from the host file_name data section
    # this is in the groups file so the host object contains this in the task
    filename = host["file_name"]
    # make the source file path eos/arista_test.txt
    dest_file = f"{platform}/{filename}-saved.txt"
    multi_result = task.run(
        task=netmiko_file_transfer,
        source_file=filename,
        dest_file=dest_file,
        direction="get",
        overwrite_file=True,
    )
    # if the result exists, then it succeeded.
    # if it doesn't then the task failed
    if multi_result[0].result is True:
        return f"SCP get operation succeeded: {dest_file}"
    else:
        return f"SCP get operation FAILED!"

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="eos"))
    result = nr.run(task=file_copy)
    print_result(result)

if __name__ == "__main__":
    main()
