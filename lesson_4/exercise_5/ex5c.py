from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks import napalm_configure

def main():

    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="arista4")
    aggr_result = nr.run(task=napalm_get, getters=["config"], retrieve="running")
    arista4_result = aggr_result["arista4"][0].result
    arista4_running_config = arista4_result["config"]["running"]

    config_string = '''interface Loopback666
    description Hello There >:)'''
    aggr_result2 = nr.run(task=napalm_configure, configuration=config_string)
    print_result(aggr_result2)

    print()
    print("-" * 50)
    print()

    aggr_result3 = nr.run(
        task=napalm_configure, configuration=arista4_running_config, replace=True
    )
    print_result(aggr_result3)


if __name__ == "__main__":
    main()