from nornir import InitNornir
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
nxos_filt = F(groups__contains="nxos")
nr = nr.filter(nxos_filt)

results = nr.run(
    task=napalm_get,
    getters="config",
    getters_options={"config": {"retrieve": "running"}}
)

print_result(results)
