import yaml
from config import playbooks_lst


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


def ssh_save_playbook(ssh, filename, pb_data):
    with ssh.open_sftp() as sftp:
        disclaimer = (
            '# This playbook was generated ONLY for specific task.\n'
            '# Do NOT use this for other tasks!\n'
            '# It can cause SERIOUS harm!\n---\n'
        )
        print(f'{playbooks_lst["yml_deploy"]}{filename}.yml')
        with sftp.open(f'{playbooks_lst["yml_deploy"]}{filename}.yml', 'w') as output_file:
            output_file.write(disclaimer)
            yaml.dump(pb_data, output_file, default_flow_style=False, sort_keys=False)

    # TODO save to db dict: pb_data.
    print(f'Playbook ui_{filename}.yml saved')
