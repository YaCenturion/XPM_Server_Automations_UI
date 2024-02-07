import json
from config import linux_packages_dict


def handler_facts(log):
    facts_str = log.split("[Display RESULT]")[1].split("=> ")[1].split("PLAY RECAP")[0].strip()
    all_facts = json.loads(facts_str)
    # print(all_facts['msg'][0])
    if 'RedHat' in all_facts['msg'][0]:
        os_family = 'redhat'
    elif 'Debian' in all_facts['msg'][0]:
        os_family = 'debian'
    else:
        return False, False

    result_data = {
        'sys': [],
        'web': [],
        'db': [],
        'other': []
    }
    for name in linux_packages_dict[os_family]:
        search_package = True
        for package, pkg_data in all_facts['msg'][1]['ansible_facts']['packages'].items():
            if name[1] == package:
                # print(f'cool: {name[0]} {name[2]} - {pkg_data[0]["version"]}')
                unit = [name[0], name[1], 'checked', pkg_data[0]["version"]]
                result_data[name[2]].append(unit)
                search_package = False
                break
        if search_package:
            unit = [name[0], name[1], '', None]
            result_data[name[2]].append(unit)

    # print(result_data)
    return True, result_data
