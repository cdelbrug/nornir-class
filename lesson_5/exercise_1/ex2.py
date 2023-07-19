from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result

def get_config(task):
    task.run(napalm_get, getters=["config"], getters_options={"config": {"retrieve": "running"}})

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(platform="eos")
    results = nr.run(task=get_config)
    print_result(results)

if "__main__" == __name__:
    main()