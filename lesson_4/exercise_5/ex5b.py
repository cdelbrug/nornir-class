from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_utils.plugins.functions import print_result

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="arista4")
    config_string = '''interface Loopback555
    description Hi There!'''
    aggr_result = nr.run(task=napalm_configure, configuration=config_string)
    print()
    print("-" * 50)
    print_result(aggr_result)
    print("-" * 50)
    print()

if __name__ == "__main__":
    main()