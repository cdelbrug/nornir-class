from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.filter import F

nr = InitNornir(config_file="config.yaml")

ios_filt = F(groups__contains="ios")
eos_filt = F(groups__contains="eos")
nr = nr.filter(ios_filt | eos_filt)

results = nr.run(
    task=napalm_get, 
    getters="arp_table",
    )

for key, value in results.items():
    print(f"Host: {key}, Gateway: {value[0].result['arp_table'][0]}")