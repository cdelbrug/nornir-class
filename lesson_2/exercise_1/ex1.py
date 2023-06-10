from nornir import InitNornir

nr = InitNornir()
# number of default workers
print(f"Number of workers: {nr.runner.num_workers}")

#nr = InitNornir(config_file="config.yml")
# print number of workers from config file
#print(f"Number of workers: {nr.runner.num_workers}")

nr = InitNornir(
    config_file="config.yml",
    runner={"plugin": "threaded", "options": {"num_workers": 15}},
)
print(f"Number of workers: {nr.runner.num_workers}")