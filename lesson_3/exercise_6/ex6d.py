from pprint import pprint
from nornir import InitNornir
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get


def main():
    nr = InitNornir(config_file="config.yaml")
    nxos_filt = F(groups__contains="nxos")
    nr = nr.filter(nxos_filt)

    results = nr.run(
        task=napalm_get,
        getters=["config", "facts"],
        # retrieve running, candidate, and startup
        getters_options={"config": {"retrieve": "all"}}
    )

    combined_data = {}

    for device_name, multi_result in results.items():

        # add dictionary equaling device name
        # and also insert empty dict inside
        combined_data[device_name] = {}
        device_result = multi_result[0]

        config_get = device_result.result["config"]

        # make every new line a list entry
        # remove first four lines for timestamp
        config_start = config_get["startup"].split("\n")[4:]
        config_running = config_get["running"].split("\n")[4:]

        fact_get = device_result.result["facts"]

        if config_running == config_start:
            combined_data[device_name]["start_running_match"] = True
        else:
            combined_data[device_name]["start_running_match"] = False

        combined_data[device_name]["vendor"] = fact_get["vendor"]
        combined_data[device_name]["model"] = fact_get["model"]
        combined_data[device_name]["uptime"] = fact_get["uptime"]

    pprint(combined_data)

if __name__ == "__main__":
    main()
