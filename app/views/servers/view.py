from flask import Blueprint, render_template, request, redirect, url_for, flash  # abort
from flask_login import current_user, login_required  # login_user, logout_user
# from sqlalchemy import desc  # func
from app import ver
from config import ansible_host, nutanix, fortigate, php_versions, web_services
from app.views.servers.ansible_utils import *
from app.views.servers.nutanix_utils import get_vms_like
from app.views.servers.servers_utils import *
from app.views.servers.ansible_patterns.roles_pattern_pool import *
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
    username = current_user.username
    front_data = {}
    # full_log = ""
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', username)
        show_post_data(request.form.items())
        target = str(request.form['ip_address']).strip()

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
                    printer(f'Update tyt')
                    update_pool = get_packages_changes(request.form.items())
                    front_data, update_logs = update_server_packages(front_data, update_pool, ssh, target, username)
                    full_log += update_logs + "=" * 30 + "\n"
                    if not front_data['update_delete'][0] or not front_data['update_install'][0]:
                        text, cat = 'Warning! Read LOG carefully!', 'error'
                    else:
                        front_data['full_log'] = [True, full_log]
                        text, cat = 'Update success!', 'success'
                    flash(text, cat)
                    
            # Ansible: Get facts
            front_data = get_facts(front_data, ssh, target, username)
            close_ssh(ssh, username)
        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text, cat = 'Warning! Read LOG carefully!', 'error'
            flash(text, cat)

    return render_template(
        'servers/server.html', query=target, data=front_data, user=current_user, ver=ver)


@login_required
@servers.route('/add_vh/', methods=['GET', 'POST'])
@servers.route('/add_vh/<target>', methods=['GET', 'POST'])
def create_vhost(target=False):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    username = current_user.username
    # target = False
    front_data = {}
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', username)
        show_post_data(request.form.items())

        target = str(request.form['ip_address']).strip()
        domain_name = str(request.form['domain_name']).strip().lower().replace('.', '_')
        web_server = str(request.form['web_service']).strip().lower()
        php_ver = str(request.form['php_ver']).strip().lower()
        # vhost_ports = str(request.form['vhost_ports']).strip().split(',')
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
                    "web_server_name": web_server,
                    # "vhost_ports": vhost_ports,
                },
                'roles': add_new_virtualhost(web_server),
            }

            # Generate playbook:
            playbook_data = generate_playbook(base_pb_pattern, playbook_sets)

            # Save playbook:
            playbook_sets['full_filename'] = ssh_save_playbook(ssh, playbook_data, playbook_sets)

            # Add to DB & Execute playbook:
            execute_pb = f'{playbooks_lst["base"]}{playbook_sets["filename"]}.yml'
            playbook_sets['command'] = f'{execute_pb} -i {target}, -e "target={target}"'
            current_task = add_task_to_db(playbook_data, playbook_sets)

            if current_task:
                status, ssh_log_facts = exec_ansible_playbook(ssh, playbook_sets['command'], username)
                current_task.status = status
                current_task.exec_log = ssh_log_facts
                db.session.commit()
            else:
                text, cat = f'ERROR: save task to DB', 'error'
                flash(text, cat)
                return redirect(url_for('.server'))

            # INFO-DELETE-ME: showing generated playbook:
            # exec_ssh_command(ssh, f'{playbooks_lst["show_me_yml"]}{playbook_sets["filename"]}.yml', username)

            # Delete playbook after execute:
            exec_ssh_command(ssh, f'{playbooks_lst["delete_yml"]}{playbook_sets["filename"]}.yml', username)

            # Ansible: Get facts
            # front_data = get_facts(front_data, ssh, target, username)

            close_ssh(ssh, username)
            text, cat = f'Done: playbook ready!', 'success'
            flash(text, cat)
            return redirect(url_for(f'.server', target=target))

        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text, cat = 'Warning! Read LOG carefully!', 'error'
            flash(text, cat)

    return render_template(
        'servers/add_new_vhost.html', query=target, data=front_data,
        php_lst=php_versions, web_service_lst=web_services, user=current_user, ver=ver)
