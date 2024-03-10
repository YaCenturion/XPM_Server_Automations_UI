import yaml

from app.utils.main_utils import save_in_db, exec_ansible_playbook, exec_ssh_command
from app.views.servers.ansible_patterns.roles_pattern_pool import base_pb_pattern
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


def generate_sub_inventory(inv_group, host_ip_address, host_desc, inv_suffix_groups):
    # Add children group
    sub_inventory = {
        "all": {
            'children': {
                inv_group: {
                    'children': {}
                }
            }
        }
    }
    
    # Add sub inventory groups
    for suffix in inv_suffix_groups:
        group_name = f"{inv_group}{suffix}"
        sub_inventory["all"]["children"][inv_group]["children"][group_name] = {
            "hosts": {
                host_ip_address: {
                    "name": host_desc,
                    "tag": suffix.replace("_", ""),
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


def inventory_to_ini(data, inventory_ini):
    for key, value in data.items():
        br = ''
        if key != 'all':
            br = '\n'
        if 'children' in data[key]:
            inventory_ini.append(f"{br}[{key}:children]")
            for child in data[key]['children'].keys():
                inventory_ini.append(f"{child}")
            
            inventory_ini = inventory_to_ini(value['children'], inventory_ini)
        if 'hosts' in data[key]:
            inventory_ini.append(f"\n[{key}]")
            for child_key, child_value in data[key]['hosts'].items():
                params = ''
                for opt, val in child_value.items():
                    params += f" {opt}={val}"
                inventory_ini.append(f"{child_key}{params}")
    
    return inventory_ini


def check_ip_address(ip_adr):
    if ip_adr.count('.') != 3 or ip_adr.count(' ') != 0:
        return False
    if len(str(ip_adr).split('.')) != 4:
        return False
    else:
        tmp = str(ip_adr).split('.')
        for i in tmp:
            if len(i) > 3 or not i.isdigit():
                return False
    return True


def pb_generate_save_execute_delete(ssh, target, playbook_sets, username):
    # Generate playbook:
    playbook_data = generate_playbook(base_pb_pattern, playbook_sets)
    # Save playbook:
    playbook_sets['full_filename'] = ssh_save_playbook(ssh, playbook_data, playbook_sets)
    # Add to DB:
    execute_pb = f'{playbooks_lst["base"]}{playbook_sets["filename"]}.yml'
    playbook_sets['command'] = f'{execute_pb} -i {target},'
    current_task = add_task_to_db(playbook_data, playbook_sets)
    
    # Execute playbook
    if current_task:
        status, ssh_log = exec_ansible_playbook(ssh, playbook_sets['command'], username)
        # status, ssh_log = True, 'Fake Log'  # Only for tests
        current_task.status = status
        current_task.exec_log = ssh_log
        db.session.commit()
        text, cat, log = 'Success! Playbook executed!', 'success', ssh_log
    else:
        text, cat, log = f'ERROR: save task to DB', 'error', False
    
    # Delete playbook after execute:
    exec_ssh_command(ssh, f'{playbooks_lst["delete_yml"]}{playbook_sets["filename"]}.yml', username)
    
    return text, cat, log


def show_playbook_yaml_code(ssh, playbook_sets, username):  # Showing generated playbook
    exec_ssh_command(ssh, f'{playbooks_lst["show_me_yml"]}{playbook_sets["filename"]}.yml', username)
    