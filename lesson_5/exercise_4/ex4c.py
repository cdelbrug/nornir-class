from nornir import InitNornir
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file

def junos_acl(task):
    #load yaml acl entries as list of dictionaries
    yaml_rules = task.run(task=load_yaml, file="rules.yaml")
    # extracting the list of dictinoaries
    rules_dict = yaml_rules[0].result
    # feeding the task the list of dictionaries called acl_file and telling it what variable it is
    multi_result = task.run(task=template_file, template="acl.j2", path=".", acl_file=rules_dict)
    task.host["acl"] = multi_result[0].result

    print()
    print("-" * 50)
    print("ACL Result")
    print(task.host["acl"])
    print("-" * 50)

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="srx2")
    nr.run(task=junos_acl)

if __name__ == "__main__":
    main()