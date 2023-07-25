from nornir import InitNornir
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_configure


def render_config(task):
    template_path = f"{task.host.platform}/"
    bgp_multi_result = task.run(task=template_file, template="bgp.j2", path=template_path, **task.host)
    int_multi_result = task.run(task=template_file, template="interface.j2", path=template_path, **task.host)
    bgp_rendered_config = bgp_multi_result[0].result
    int_rendered_config = int_multi_result[0].result
    # add a dictionary key under the task.host var and put in the rendered config
    task.host["bgp_rendered_config"] = bgp_rendered_config
    task.host["int_rendered_config"] = int_rendered_config

def write_configs(task):
    cfg_path = "rendered_configs/"
    bgp_filename = f"{cfg_path}{task.host.name}_bgp"
    int_filename = f"{cfg_path}{task.host.name}_int"
    bgp_content = task.host["bgp_rendered_config"]
    int_content = task.host["int_rendered_config"]
    task.run(task=write_file, filename=bgp_filename, content=bgp_content)
    task.run(task=write_file, filename=int_filename, content=int_content)

def deploy_config(task):
    bgp_filename = f"rendered_configs/{task.host.name}_bgp"
    int_filename = f"rendered_configs/{task.host.name}_int"
    with open(bgp_filename, "r") as fbgp, open(int_filename, "r") as fint:
        bgp_data = fbgp.read()
        int_data = fint.read()
    configure = ""
    configure += bgp_data
    configure += "\n"
    configure += int_data
    result = task.run(task=napalm_configure, configuration=configure)
    return result

def verify_bgp_status(task):
    pass

def main():
    nr = InitNornir(config_file="config.yaml")
    # doesn't work for some reason!?
#    nr = nr.filter(platform="cisco_nxos")
    nr = nr.filter(F(groups__contains="nxos"))
    render_result = nr.run(task=render_config)
    write_result = nr.run(task=write_configs)
    deploy_result = nr.run(task=deploy_config)

if __name__ == "__main__":
    main()