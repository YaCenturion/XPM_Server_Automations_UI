import json
from app.utils.main_utils import *
from config import linux_packages_dict, playbooks_lst


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
                unit = [name[0], name[1], 'checked', pkg_data[0]["version"]]
                result_data[name[2]].append(unit)
                search_package = False
                break
        if search_package:
            unit = [name[0], name[1], '', None]
            result_data[name[2]].append(unit)

    # print(result_data)
    return True, result_data


def get_packages_changes(form_data):
    update_pool = {'delete': [], 'install': []}
    for key, value in form_data:
        if value == '+set':
            update_pool['install'].append(key)
        elif value == '-del':
            update_pool['delete'].append(key)
    return update_pool


def update_server_packages(front_data, update_pool, ssh, target, username):
    full_log = ''
    front_data['update_delete'] = [True, 'Not used']
    front_data['update_install'] = [True, 'Not used']
    first_block = f'{playbooks_lst["base"]}{playbooks_lst["action"]} -i {target}, -e "target={target} packages='
    if update_pool['delete']:
        pkg_names_pool = ','.join(update_pool['delete'])
        ''' -i 172.17.188.226, -e "target=172.17.188.226 packages=git action=latest"'''
        command = first_block + f'{pkg_names_pool} action=absent"'
        status_remove, ssh_log_remove = exec_ansible_playbook(ssh, command, username)
        full_log += ssh_log_remove
        front_data['update_delete'] = [status_remove, ssh_log_remove]
    if update_pool['install']:
        pkg_names_pool = ','.join(update_pool['install'])
        command = first_block + f'{pkg_names_pool} action=latest"'
        status_install, ssh_log_install = exec_ansible_playbook(ssh, command, username)
        full_log += ssh_log_install
        front_data['update_install'] = [status_install, ssh_log_install]
    return front_data, full_log


def get_facts(front_data, ssh, target, username):
    front_data['packages'] = False
    command = f'{playbooks_lst["base"]}{playbooks_lst["get_facts"]} -i {target}, -e "target={target}"'
    status_get_facts, ssh_log_facts = exec_ansible_playbook(ssh, command, username)
    
    if status_get_facts:
        result, data_pool = handler_facts(ssh_log_facts)
        if result:
            front_data['packages'] = data_pool
    
    front_data['get_facts'] = [status_get_facts, ssh_log_facts]
    return front_data
