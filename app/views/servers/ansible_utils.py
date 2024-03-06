import yaml

from app.utils.main_utils import save_in_db
from config import playbooks_lst
from app.models import *


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


def generate_playbook(playbook_data, playbook_sets):
    playbook_data[0]['name'] = playbook_sets['name']
    playbook_data[0]['hosts'] = playbook_sets['target']
    playbook_data[0]['remote_user'] = 'xpmans'
    playbook_data[0]['become'] = True
    playbook_data[0]['vars'] = {'state_action': "{{ state_action | default('___NOT_SET___') }}"}
    playbook_data[0]['roles'] = []
    if 'vars' in playbook_sets:
        playbook_data[0]['vars'] = playbook_sets['vars']

    for role_set in playbook_sets['roles']:
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
        # print(f"Append: {role}")
        playbook_data[0]['roles'].append(role)
    return playbook_data


def ssh_save_playbook(ssh, pb_data, pb_sets):
    full_filename = f'{playbooks_lst["prod_deploy"]}{pb_sets["filename"]}.yml'
    with ssh.open_sftp() as sftp:
        disclaimer = (
            f'# Generated in OpsUI app: {full_filename}\n'
            '# This playbook was generated ONLY for specific task.\n'
            '# Do NOT use this playbook for other tasks!\n'
            '# Powerful witchcraft - using a level 99 spell!\n'
            '# It can cause SERIOUS DAMAGE!\n#\n---\n'
        )
        # print(f'{playbooks_lst["prod_deploy"]}{filename}.yml')
        with sftp.open(full_filename, 'w') as output_file:
            output_file.write(disclaimer)
            yaml.dump(pb_data, output_file, default_flow_style=False, sort_keys=False)
    return full_filename


def add_task_to_db(pb_data, pb_sets):
    new_task = TasksHistory(
        user_id=pb_sets['user_id'],
        username=pb_sets['username'],
        host=pb_sets['target'],
        # status=None,
        exec_time=int(time.time()),
        exec_filename=pb_sets['filename'],
        exec_command=pb_sets['command'],
        exec_title=pb_sets['name'],
        exec_code=yaml.dump(pb_data, default_flow_style=False, sort_keys=False),
        # exec_log=exec_log,
        # comments=comments
    )
    task = save_in_db(new_task)
    return task


def generate_inventory(inv_group, host_ip_address, host_desc, inv_sub_groups):
    sub_inventory = {}

    # Add children group
    children_group = f"{inv_group}:children"
    sub_inventory[children_group] = {f"{inv_group}{sub_group}" for sub_group in inv_sub_groups}

    # Add sub inventory groups
    for sub_group in inv_sub_groups:
        sub_group_name = f"{inv_group}{sub_group}"
        sub_inventory[sub_group_name] = {
            "hosts": {
                host_ip_address: {
                    "name": host_desc
                }
            }
        }

    return sub_inventory


def merge_inventory(current_inventory, sub_inv):
    updated_inventory = current_inventory.copy()
    for key, value in sub_inv.items():
        if key in updated_inventory:
            if isinstance(value, dict) and isinstance(updated_inventory[key], dict):
                updated_inventory[key] = merge_inventory(updated_inventory[key], value)
            else:
                updated_inventory[key] = value
        else:
            updated_inventory[key] = value
    return updated_inventory
