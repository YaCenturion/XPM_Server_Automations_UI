import yaml
from app.views.servers.ansible_patterns.roles_pattern_pool import *


def build_role_line(role_pattern, vars_update=None, state_action=None):
    if vars_update is not None:
        for var in vars_update:
            for key, value in role_pattern['vars'].items():
                if key == var[0]:
                    # print(role_pattern)
                    role_pattern['vars'][key] = var[1]
            if var[0] not in role_pattern['vars']:
                role_pattern['vars'][var[0]] = var[1]

    if 'directory' in role_pattern['role'] and state_action is not None:
        role_pattern['vars']['state_action'] = state_action
    return role_pattern


def generate_playbook(base_pattern_pb, pb_name, roles_list, v_data=None):
    base_pattern_pb[0]['name'] = pb_name
    if v_data is not None:
        base_pattern_pb[0]['vars'] = v_data
    for role_set in roles_list:
        state_action = None
        if 'state_action' in base_pattern_pb[0]['vars']:
            if base_pattern_pb[0]['vars']['state_action'] == 'present':
                if 'directory' in role_set[0]['role']:
                    state_action = 'directory'
        role = build_role_line(role_set[0], role_set[1], state_action)
        base_pattern_pb[0]['roles'].append(role)
    return base_pattern_pb


def save_playbook(ssh, filename, pb_data):
    with open(f'ansible_patterns/temp/{filename}.yml', 'w', encoding='utf-8') as output_file:
        yaml.dump(pb_data, output_file, default_flow_style=False, sort_keys=False)
    # TODO save to db dict: pb_data.
    print(f'Playbook {filename}.yml saved')


if __name__ == '__main__':
    pool = [
        (r_system['user'], [['state_action', "present"], ['foo_action', "present"]]),
        (r_system['directory'], [['state_action', "present"]]),
        (r_system['install_mysql_module'], None),
        (r_db['db'], None),
        (r_db['user'], None),
        (r_web['create_php_fpm_sock'], None),
        (r_web['SSL_certificate'], None),
        (r_web['create_apache_virtualhost'], None),
        (r_web['ftp_user'], None),
        (r_web['restart_apache'], None),
    ]

    vars_data = {
        "state_action": 'present',
        "username": 'root',
        "password": '<PASSWORD>',
        "domain": 'domain.co.il'
    }

    result = generate_playbook(base_pattern, 'THIS IS NAME', pool, v_data=vars_data)
    save_playbook('will be ssh', 'new_filename', result)
