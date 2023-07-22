from nornir import InitNornir
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_string

# looping over list of dictionaries
# grabbing acl name dict key, then the value is a list of acl_rules in the acl_file var
# looping through list of rules and inserting vars
TEMPLATE_STR = """
    {% for acl_name, acl_rules in acl_file.items() %}
        {% for acl_rule in acl_rules %}
        set firewall family inet filter {{ acl_name }} term {{ acl_rule['term_name'] }} from protocol {{ acl_rule['protocol'] }}
        set firewall family inet filter {{ acl_name }} term {{ acl_rule['term_name'] }} from protocol {{ acl_rule['destination_port'] }}
        set firewall family inet filter {{ acl_name }} term {{ acl_rule['term_name'] }} from protocol {{ acl_rule['destination_address'] }}"
        set firewall family inet filter {{ acl_name }} term {{ acl_rule['term_name'] }} from protocol {{ acl_rule['destination_address'] }}"
        set firewall family inet filter {{ acl_name }} term {{ acl_rule['term_name'] }} from protocol {{ acl_rule['state'] }}"
        {% endfor %}
    {% endfor %}
        """

def junos_acl(task):
    #load yaml acl entries as list of dictionaries
    yaml_rules = task.run(task=load_yaml, file="rules.yaml")
    # extracting the list of dictinoaries
    rules_dict = yaml_rules[0].result
    # feeding the task the list of dictionaries called acl_file and telling it what variable it is
    multi_result = task.run(task=template_string, template=TEMPLATE_STR, acl_file=rules_dict)

    print()
    print("-" * 50)
    print("ACL Result")
    print(multi_result[0].result)
    print("-" * 50)

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="srx2")
    nr.run(task=junos_acl)

if __name__ == "__main__":
    main()