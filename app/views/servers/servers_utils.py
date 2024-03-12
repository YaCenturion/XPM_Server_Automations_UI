import json
from flask import redirect, url_for, flash
from app.utils.main_utils import *
from app.views.servers.ansible_patterns.roles_pattern_pool import packages_action, roles
from app.views.servers.ansible_utils import pb_generate_save_execute_delete
from config import linux_packages_dict, playbooks_lst


def handler_facts(log):
    facts_str = log.split("Display RESULT")[1].split("=> ")[1].split("PLAY RECAP")[0].strip()
    all_facts = json.loads(facts_str)
    main_facts = all_facts['msg'][0]

    if not main_facts['family'].lower() in linux_packages_dict:
        return False, False

    packages_facts = {
        'sys': [],
        'web': [],
        'db': [],
        'other': []
    }
    for name in linux_packages_dict[main_facts['family'].lower()]:
        search_package = True
        for package, pkg_data in all_facts['msg'][1]['ansible_facts']['packages'].items():
            if name[1] == package:
                unit = [name[0], name[1], 'checked', pkg_data[0]["version"]]
                packages_facts[name[2]].append(unit)
                search_package = False
                break
        if search_package:
            unit = [name[0], name[1], '', None]
            packages_facts[name[2]].append(unit)

    data = [
        main_facts,
        packages_facts,
        all_facts['msg'][2],
        all_facts['msg'][3],
        all_facts['msg'][4],
        all_facts['msg'][5],
        all_facts['msg'][6],
    ]
    return True, data


def get_packages_changes(form_data):
    update_pool = {'delete': [], 'install': []}
    for key, value in form_data:
        if value == '+set':
            update_pool['install'].append(key)
        elif value == '-del':
            update_pool['delete'].append(key)
    if 'httpd' in update_pool['delete']:
        update_pool['delete'].append('httpd-tools')
        update_pool['delete'].append('httpd-manual')
    return update_pool


def add_packages_action(packages, action):
    additional_role = False
    for package in packages:
        if package in ('apache2', 'httpd'):
            if action == 'absent':
                additional_role = roles['web']["apache_cleaner"]
            elif action == 'latest':
                additional_role = roles['web']["apache_default"]
            else:
                additional_role = False
        elif package == 'nginx':
            if action == 'absent':
                additional_role = roles['web']["nginx_cleaner"]
            elif action == 'latest':
                additional_role = roles['web']["nginx_default"]
            else:
                additional_role = False

    return additional_role


def update_server_packages(front_data, update_pool, ssh, target, ui_usr):
    def packages_action_playbook(state, pkg_pool, addons=False):
        pb_sets = {
            'user_id': ui_usr['id'],
            'username': ui_usr['name'],
            'filename': f"{str(int(time.time()))}_{target}",
            'name': f'Update packages for: {target}',
            'target': target,
            'vars': {
                "packages": pkg_pool,
                "action": state,
            },
            'roles': packages_action(addons),
        }
        return pb_sets
    
    full_log = ''
    front_data['update_delete'] = [True, 'Not used']
    front_data['update_install'] = [True, 'Not used']

    if update_pool['delete']:
        action = "absent"
        pkg_names_pool = ','.join(update_pool['delete'])
        additional_role = add_packages_action(update_pool['delete'], action)
        playbook_sets = packages_action_playbook(action, pkg_names_pool, additional_role)
        text, cat, ssh_log = pb_generate_save_execute_delete(ssh, target, playbook_sets, ui_usr['name'])
        full_log += ssh_log
        
        status = True
        if cat == 'error':
            status = False
        front_data['update_delete'] = [status, ssh_log]
    if update_pool['install']:
        action = "latest"
        pkg_names_pool = ','.join(update_pool['install'])
        additional_role = add_packages_action(update_pool['install'], action)
        playbook_sets = packages_action_playbook(action, pkg_names_pool, additional_role)
        text, cat, ssh_log = pb_generate_save_execute_delete(ssh, target, playbook_sets, ui_usr['name'])
        full_log += ssh_log

        status = True
        if cat == 'error':
            status = False
        front_data['update_install'] = [status, ssh_log]
    return front_data, full_log


def get_facts(front_data, ssh, target, username):
    front_data['packages'] = False
    command = f'{playbooks_lst["base"]}{playbooks_lst["get_facts"]} -i {target}, -e "target={target}"'
    status_get_facts, ssh_log_facts = exec_ansible_playbook(ssh, command, username)
    # print(status_get_facts)
    if status_get_facts:
        result, data_pool = handler_facts(ssh_log_facts)
        if result:
            front_data['system'] = data_pool[0]
            front_data['packages'] = data_pool[1]
            front_data['all_ipv4'] = data_pool[2]
            front_data['ports'] = data_pool[3]
            front_data['mounts'] = data_pool[4]
            front_data['php_fpm_versions'] = data_pool[5]
            front_data['php_fpm_services'] = data_pool[6]
        else:
            status_get_facts = False
            front_data['system'] = False
            front_data['packages'] = False
            front_data['all_ipv4'] = False
            front_data['ports'] = False
            front_data['mounts'] = False
            front_data['php_fpm_versions'] = False
            front_data['php_fpm_services'] = False
    else:
        text, cat = f'Error SSH to server: {target}!', 'error'
        flash(text, cat)
    
    front_data['get_facts'] = [status_get_facts, ssh_log_facts]
    if 'full_log' in front_data:
        # print('=====================>>>', front_data['full_log'])
        front_data['full_log'][0] = status_get_facts
        front_data['full_log'][1] += ssh_log_facts
    else:
        front_data['full_log'] = [status_get_facts, ssh_log_facts]

    return front_data


def get_vip_like(ip_address):
    results_vip = VirtualIps.query.filter(
        (VirtualIps.virtual_ip.ilike(f"%{ip_address}%")) |
        (VirtualIps.internal_ip.ilike(f"%{ip_address}%"))).first()
    if results_vip is None:
        results_vip = False
    return results_vip
