from nornir import InitNornir
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_string


TEMPLATE_STR = """
                set firewall family inet filter {{ acl_name }} term {{ acl_entry['term_name'] }} from protocol {{ acl_entry['protocol'] }}
                set firewall family inet filter {{ acl_name }} term {{ acl_entry['term_name'] }} from protocol {{ acl_entry['destination_port'] }}
                set firewall family inet filter {{ acl_name }} term {{ acl_entry['term_name'] }} from protocol {{ acl_entry['destination_address'] }}"
                set firewall family inet filter {{ acl_name }} term {{ acl_entry['term_name'] }} from protocol {{ acl_entry['destination_address'] }}"
                set firewall family inet filter {{ acl_name }} term {{ acl_entry['term_name'] }} from protocol {{ acl_entry['state'] }}"
                """

def junos_acl(task):
    #load yaml acl entries as list of dictionaries
    in_yaml = task.run(task=load_yaml, file="rules.yaml")
    # extract list of dictionaries
    in_yaml = in_yaml[0].result
    return in_yaml

def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="srx2")
    nr.run(task=junos_acl)
    result = nr.run(task=template_string, template=TEMPLATE_STR)
    print(result)

if __name__ == "__main__":
    main()