from flask import Blueprint, render_template, request  # , redirect, url_for, flash  # abort
from flask_login import current_user, login_required  # login_user, logout_user
# from sqlalchemy import desc  # func
# import yaml
from app import ver
from config import ansible_host, nutanix, fortigate, php_versions, web_services
from app.views.servers.ansible_utils import *
from app.views.servers.nutanix_utils import get_vms_like
from app.views.servers.servers_utils import *
from app.views.servers.ansible_patterns.roles_pattern_pool import *
from app.views.servers.logs_utils import get_action_logs
from app.utils.main_utils import *
from app.views.servers.update_utils import *
# from app import client_pay_status_lst

servers = Blueprint('servers', __name__)


@login_required
@servers.route('/update_db/', methods=['GET', 'POST'])
def update_db():
    """ Update the forti and nutanix"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    result, update_log = start_update(fortigate, nutanix)
    if result:
        print('Update DB - ok!')
        text, cat = 'DB updated', 'success'
    else:
        text, cat = 'BAD UPDATE!', 'error'
        print(update_log)
        print('Rows from Nutanix', len(NutanixVMs.query.all()))
        print('Rows from Fortigate', len(VirtualIps.query.all()))
    
    flash(text, cat)
    return redirect(url_for('.server'))


@login_required
@servers.route('/server/<string:target>', methods=['GET', 'POST'])
@servers.route('/server', methods=['GET', 'POST'])
def server(target=False):
    """ Server details and actions """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    ui_usr = {
        'name': current_user.username,
        'id': current_user.id,
    }
    front_data = {}
    # full_log = ""
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', ui_usr['name'])
        show_post_data(request.form.items())
        target, target_port = target_filter(str(request.form['ip_address']).strip().replace(',', '.'))
        if target_port == 'error':
            flash(target, target_port)
            return redirect(url_for('.server'))

    if target:
        front_data['vms'] = get_vms_like(target)
        front_data['v_ip'] = get_vip_like(target)
        printer(f"Get VIP: {front_data['v_ip']}")
        ssh, msg = get_ssh(ansible_host)

        if ssh:
            full_log = ""
            # Ansible: Update packages
            if 'update' in request.form:
                if request.form['update'] == 'true':
                    printer(f'User starting to update packages')
                    update_pool = get_packages_changes(request.form.items())
                    front_data, update_logs = update_server_packages(front_data, update_pool, ssh, target, ui_usr)
                    full_log += update_logs + "=" * 30 + "\n"
                    if not front_data['update_delete'][0] or not front_data['update_install'][0]:
                        text, cat = 'Warning! Read LOG carefully!', 'error'
                    else:
                        front_data['full_log'] = [True, full_log]
                        text, cat = 'Update success!', 'success'
                    flash(text, cat)
                    
            # Ansible: Get facts
            front_data = get_facts(front_data, ssh, target, ui_usr['name'])
            close_ssh(ssh, ui_usr['name'])
        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text, cat = 'Maybe not under Ansible control yet.', 'error'
            flash(text, cat)
            return redirect(url_for('.get_ansible_control', target=target))

    return render_template(
        'servers/server.html', query=target, data=front_data, user=current_user, ver=ver)


@login_required
@servers.route('/add_vh/<target>', methods=['GET', 'POST'])
@servers.route('/add_vh/', methods=['GET', 'POST'])
def create_vhost(target=False):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    ui_usr = {
        'name': current_user.username,
        'id': current_user.id,
    }
    front_data = {}
    php_fpm_lst = php_versions
    php_fpm_old_path = False
    if target:
        if not check_ip_address(target):
            text, cat = f'ERROR in IP-address', 'error'
            flash(text, cat)
            return redirect(url_for('.add_vhost'))
        ssh, msg = get_ssh(ansible_host)
        front_data = get_facts(front_data, ssh, target, ui_usr['name'])

        php_fpm_lst = get_php_fpm_installed(front_data['php_fpm_versions'])
        if not php_fpm_lst:
            php_fpm_lst = php_versions
        php_fpm_old_path = get_php_fpm_path(front_data['php_fpm_services'])

    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', ui_usr['name'])
        show_post_data(request.form.items())
        
        # Vars from form
        target, target_port = target_filter(str(request.form['ip_address']).strip().replace(',', '.'))
        if target_port == 'error':
            flash(target, target_port)
            return redirect(url_for('.add_vhost'))
        domain_name = str(request.form['domain_name']).strip().lower()  # .replace('.', '_')
        web_server = str(request.form['web_service']).strip().lower()
        php_ver = str(request.form['php_ver']).strip().lower()
        db_user = str(request.form['db_user']).strip().lower().replace('.', '_')
        db_pass = str(request.form['db_pass']).strip()
        
        ssh, msg = get_ssh(ansible_host)
        if ssh:
            # Ansible:
            # Setup new VirtualHost
            playbook_sets = {
                'user_id': current_user.id,
                'username': current_user.username,
                'filename': f"{str(int(time.time()))}_{domain_name.lower().replace('.', '_')}",
                'name': f'Add new VirtualHost for: {domain_name}',
                'target': target,
                'vars': {
                    "state_action": 'present',
                    "username": domain_name,
                    "mysql_user": db_user,
                    "mysql_pass": db_pass,
                    "selected_php": php_ver,
                    "use_php_fpm_old_path": php_fpm_old_path,
                    "web_server_name": web_server,
                },
                'roles': add_new_virtualhost(web_server),
            }
            
            text, cat, log = pb_generate_save_execute_delete(ssh, target, playbook_sets, ui_usr['name'])
            flash(text, cat)
            if cat in ('error', 'warning'):
                return redirect(url_for('.server'))

            # show_playbook_yaml_code(ssh, playbook_sets, username)  # Showing generated playbook

            close_ssh(ssh, ui_usr['name'])
            flash(text, cat)
            return redirect(url_for(f'.server', target=target))

        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text, cat = 'Warning! Read LOG carefully!', 'error'
            flash(text, cat)

    return render_template(
        'servers/add_new_vhost.html', query=target, data=front_data,
        php_lst=php_fpm_lst, web_service_lst=web_services, user=current_user, ver=ver)


@login_required
@servers.route('/get_ansible_control/<string:target>', methods=['GET', 'POST'])
@servers.route('/get_ansible_control/', methods=['GET', 'POST'])
def get_ansible_control(target=False):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    ui_usr = {
        'name': current_user.username,
        'id': current_user.id,
    }
    front_data = {}
    ssh, msg = get_ssh(ansible_host)
    if not ssh:
        flash('Error SSH to Ansible server! Impossible use services...', 'error')
        flash(f'Error log: {msg}', 'error')
        return redirect(url_for('.server'))
    
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', ui_usr['name'])
        show_post_data(request.form.items())
        
        # Vars from form
        target, target_port = target_filter(str(request.form['ip_address']).strip().replace(',', '.'))
        if target_port == 'error':
            flash(target, target_port)
            return redirect(url_for('.get_ansible_control'))
        host_desc = str(request.form['host_desc']).strip().replace('-', '_').replace(' ', '_')
        remote_user_login = str(request.form['remote_user_login']).strip()
        remote_user_pass = str(request.form['remote_user_login']).strip()
        inv_group = str(request.form['inv_group']).strip().replace('-', '_').replace(' ', '_')
        inv_sub_groups = []
        sub_group_keys = [key for key in request.form.keys() if key.startswith('sub_group_')]
        for key in sub_group_keys:
            value = request.form[key]
            inv_sub_groups.append(value)

        # Ansible:
        # Get inventory
        inventory_yaml = get_ansible_inventory(ssh, 'yaml')
        filename_inv = "backups/inventory/ansible_inventory"
        if inventory_yaml:
            current_inventory = yaml.safe_load(inventory_yaml)

            with open(f'{filename_inv}_backup.yaml', 'w') as file:  # Save backup Local
                yaml.dump(current_inventory, file, default_flow_style=False)
        else:
            text, cat = f'ERROR when get inventory', 'error'
            flash(text, cat)
            return redirect(url_for('.get_ansible_control'))

        # Get ansible control under server
        playbook_sets = {
            'user_id': current_user.id,
            'username': current_user.username,
            'filename': f"{str(int(time.time()))}_injection_{target.lower().replace('.', '_')}",
            'name': f'Get Ansible control under server: {target}',
            'target': target,
            'vars': {
                "remote_user_login": remote_user_login,
                "remote_user_pass": remote_user_pass,
            },
            'roles': injection_ansible_control(),
        }
        
        text, cat, log = pb_generate_save_execute_delete(ssh, target, playbook_sets, ui_usr['name'])
        flash(text, cat)
        if cat in ('error', 'warning'):
            return redirect(url_for('.server'))

        # show_playbook_yaml_code(ssh, playbook_sets, username)  # Showing generated playbook

        # Update inventory
        sub_inv = generate_sub_inventory(inv_group, target, host_desc, inv_sub_groups)
        inventory = merge_inventory(current_inventory, sub_inv)
        
        # Convert to INI
        inventory_ini = '\n'.join(inventory_to_ini(inventory, [])) + '\n'

        # BackUp & Deploy inventory
        deploy_updated_inventory(ssh, inventory, inventory_ini, ui_usr['name'])

        # Local saving inventory
        save_inventory_local(filename_inv, inventory, inventory_ini)

        close_ssh(ssh, ui_usr['name'])
        text += ' Inventory updated!'
        flash(text, cat)
        return redirect(url_for('.server', target=target))
    
    else:
        inventory_json = json.loads(get_ansible_inventory(ssh, 'export'))
        ansible_groups = inventory_json['all']['children']
        close_ssh(ssh, ui_usr['name'])
        # print(ansible_groups, type(ansible_groups))
        
    return render_template(
        'servers/get_ansible_control.html', query=target, data=front_data,
        ansible_groups=ansible_groups, php_lst=php_versions, web_service_lst=web_services,
        user=current_user, ver=ver)


@login_required
@servers.route('/action_logs/', methods=['GET', 'POST'])
@servers.route('/action_logs/<int:limiter>', methods=['GET', 'POST'])
def action_logs(limiter=100):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    ui_usr = {
        'name': current_user.username,
        'id': current_user.id,
    }
    front_data = {}
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', ui_usr['name'])
        show_post_data(request.form.items())

    front_data['action_logs'] = get_action_logs(limiter)
    return render_template(
        'servers/actions_log.html', data=front_data, user=current_user, ver=ver)
