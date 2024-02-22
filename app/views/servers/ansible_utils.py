import yaml
from app.views.servers.ansible_patterns.roles_pattern_pool import *


def build_role_data(role_pattern, role_vars=None, state_action=None):
    if role_vars is not None:
        if 'vars' in role_pattern:
            role_pattern['vars'].update(role_vars)
        else:
            role_pattern['vars'] = role_vars

    if 'directory' in role_pattern['role'] and state_action is not None:
        if 'vars' in role_pattern:
            role_pattern['vars']['state_action'] = state_action
        else:
            role_pattern['vars'] = {'state_action': state_action}
    return role_pattern


def generate_playbook(playbook_data, target, name_value, roles_list, v_data=None):
    playbook_data[0]['name'] = name_value
    playbook_data[0]['hosts'] = target
    if v_data is not None:
        playbook_data[0]['vars'] = v_data

    for role_set in roles_list:
        role_vars = None
        if len(role_set) > 1:
            role_vars = role_set[1]
        role_preset = role_set[0]
        """ Part for search state_actions for directory roles"""
        new_state_action = None
        if 'state_action' in playbook_data[0]['vars']:
            if playbook_data[0]['vars']['state_action'] == 'present':
                if 'directory' in role_preset['role']:
                    new_state_action = 'directory'

        role = build_role_data(role_preset, role_vars, new_state_action)
        playbook_data[0]['roles'].append(role)
    return playbook_data


def save_playbook(ssh, filename, pb_data):
    print(ssh)
    disclaimer = (
        '# This playbook was generated ONLY for specific task.\n'
        '# Do NOT use this for other tasks!\n'
        '# It can cause SERIOUS harm!\n---\n'
    )
    with open(f'ansible_patterns/temp/{filename}.yml', 'w', encoding='utf-8') as output_file:
        output_file.write(disclaimer)
        yaml.dump(pb_data, output_file, default_flow_style=False, sort_keys=False)
    # TODO save to db dict: pb_data.
    print(f'Playbook {filename}.yml saved')


if __name__ == '__main__':
    tasks = [
        # (r_system['user'], {'test1': "aaa", 'test2': "yes", 'test3': 8989898}),  # example for add specials role vars
        (r_system['user'],),
        (r_system['directory'],),
        (r_system['install_mysql_module'],),
        (r_db['db'],),
        (r_db['user'],),
        (r_web['create_php_fpm_sock'],),
        (r_web['SSL_certificate'],),
        (r_web['create_apache_virtualhost'],),
        (r_web['ftp_user'],),
        (r_web['restart_apache'],),
    ]

    target_query = '192.168.2.1'
    glob_vars_data = {

        "state_action": 'present',
        "mysql_user": 'root',
        "mysql_pass": '<PASSWORD>',
        "username": 'domain.co.il',
    }

    playbook_filename = 'ansible_test'
    playbook_name = '== THIS IS PLAYBOOK NAME. GENERATED FOR TEST =='
    result = generate_playbook(base_pattern, target_query, playbook_name, tasks, glob_vars_data)
    save_playbook('will be ssh', playbook_filename, result)
