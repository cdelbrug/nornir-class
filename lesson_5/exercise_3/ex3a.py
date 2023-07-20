from nornir import InitNornir
from nornir_utils.plugins.tasks.data import load_yaml

def junos_acl(task):
    #load yaml acl entries as list of dictionaries
    in_yaml = task.run(task=load_yaml, file="rules.yaml")
    # extract list of dictionaries
    in_yaml = in_yaml[0].result
    rules = []

    # acl_name is my_acl, then acl_entries are the list dictionary entries for each line
    # not sure what the difference is in using items() than just the in_yaml
    #returns a tuple
    for acl_name, acl_entries in in_yaml.items():
        # go through each rule entry in the dictionary list
        for acl_entry in acl_entries:
            rules.append(
                # line breaks are for formatting the code, still one line in output.
                f"set firewall family inet filter {acl_name} term {acl_entry['term_name']} "
                f"from protocol {acl_entry['protocol']}"
            )
            rules.append(
                f"set firewall family inet filter {acl_name} term {acl_entry['term_name']} "
                f"from destination-port {acl_entry['destination_port']}"
            )
            rules.append(
                f"set firewall family inet filter {acl_name} term {acl_entry['term_name']} "
                f"from destination-address {acl_entry['destination_address']}"
            )
            rules.append(
                f"set firewall family inet filter {acl_name} term {acl_entry['term_name']} "
                f"then {acl_entry['state']}"
            )

        print()
        print("#" * 80)
        for rule in rules:
            print(rule)
        print("#" * 80)
        print()


def main():
    nr = InitNornir(config_file="config.yaml")
    nr = nr.filter(name="srx2")
    nr.run(task=junos_acl)

if __name__ == "__main__":
    main()