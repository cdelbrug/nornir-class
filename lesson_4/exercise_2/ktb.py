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
    source_file = f"{platform}/{filename}"
    task.run(
        task=netmiko_file_transfer,
        source_file=source_file,
        dest_file=filename,
        direction="put",
        overwrite_file=True,
    )

    # def verify_file(task):
    # import ipdb; ipdb.set_trace()
    cmd = f"more flash:/{filename}"
    multi_result = task.run(task=netmiko_send_command, command_string=cmd)
    output = multi_result[0].result
    print()
    print("-" * 50)
    print(f"{task.host}")
    print("-" * 50)
    print()
    print(output)
    print()


def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(F(groups__contains="eos"))
    result = nr.run(task=file_copy)
    print_result(result)
    # verify = nr.run(task=verify_file)
    # print_result(verify)


if __name__ == "__main__":
    main()
