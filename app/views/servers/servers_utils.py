import json
from config import linux_packages_dict


def handler_facts(log):
    facts_str = log.split("[Display RESULT]")[1].split("=> ")[1].split("PLAY RECAP")[0].strip()
    all_facts = json.loads(facts_str)
    print(all_facts['msg'][0])
    if 'RedHat' in all_facts['msg'][0]:
        os_family = 'redhat'
    elif 'Debian' in all_facts['msg'][0]:
        os_family = 'debian'
    else:
        return False, False

    for name in linux_packages_dict[os_family].keys():
        for package in all_facts['msg'][1]['ansible_facts']['packages'].keys():
            ''' Перебрать два словаря'''
            # linux_packages_dict[os_family][name]

    pass
