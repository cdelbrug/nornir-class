from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir.core.exceptions import NornirSubTaskError


def render_config(task):
    # feed in the data variables in the inventory file from the task.host var (current host in task)
    try:
        intf_multi_result = task.run(task=template_file, template="intf.j2", path=".", **task.host)
        # extract config rendered
        int_rendered_config = intf_multi_result[0].result
    except NornirSubTaskError as e:
        print(f"Subtask error: {e}")


def main():
    nr = InitNornir(config_file="config.yaml")
    # doesn't work for some reason!?
#    nr = nr.filter(platform="cisco_nxos")
    nr = nr.filter(F(groups__contains="nxos"))
    render_result = nr.run(task=render_config)
    #print(render_result)
    print_result(render_result)

if __name__ == "__main__":
    main()