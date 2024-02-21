from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required  # login_user, logout_user
# from sqlalchemy import desc  # func
from app import ver
from app.views.servers.nutanix_utils import get_vms_like
from app.views.servers.servers_utils import *
from config import ansible_host, playbooks_lst, nutanix, fortigate
from app.utils.main_utils import *
from app.views.servers.update_utils import *
# from app import client_pay_status_lst

servers = Blueprint('servers', __name__)


@login_required
@servers.route('/up/', methods=['GET', 'POST'])
def update_db():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if start_update(fortigate, nutanix):
        text, cat = 'DB updated', 'success'
    else:
        text, cat = 'BAD UPDATE!', 'error'
    flash(text, cat)
    return redirect(url_for('servers.server'))


@login_required
@servers.route('/server/', methods=['GET', 'POST'])
def server():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    username = current_user.username
    target = False
    front_data = {}
    # full_log = ""
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', username)
        show_post_data(request.form.items())
        
        target = str(request.form['ip_address']).strip()
        front_data['vms'] = get_vms_like(target)
        # front_data['v_ips'] = get_vips_like(target)
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
@servers.route('/vhost/', methods=['GET', 'POST'])
def create_vhost():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    username = current_user.username
    target = False
    front_data = {}
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', username)
        show_post_data(request.form.items())

        target = str(request.form['ip_address']).strip()
        domain_name = str(request.form['domain_name']).strip().lower().replace('.', '_')
        ssh, msg = get_ssh(ansible_host)

        if ssh:
            # Ansible: Setup vhost
            # TODO here
            print(domain_name)
            print(generate_password(15))

            # Ansible: Get facts
            front_data = get_facts(front_data, ssh, target, username)
            close_ssh(ssh, username)
        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text, cat = 'Warning! Read LOG carefully!', 'error'
            flash(text, cat)

    return render_template(
        'servers/vhost.html', query=target, data=front_data, user=current_user, ver=ver)
