from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required  # login_user, logout_user
# from sqlalchemy import desc  # func
from app import ver
from app.views.servers.servers_utils import *
from config import ansible_host, playbooks_lst
from app.utils.main_utils import *
# from app import client_pay_status_lst

servers = Blueprint('servers', __name__)


@login_required
@servers.route('/warm_up/', methods=['GET', 'POST'])
def warm_up():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    username = current_user.username
    target = False
    front_data = {}
    full_log = ""
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', username)
        show_post_data(request.form.items())
        
        target = str(request.form['ip_address']).strip()
        ssh, msg = get_ssh(ansible_host)

        if ssh:
            full_log = "=" * 30 + "\n"
            # Ansible: Update packages
            if 'update' in request.form:
                if request.form['update'] == 'true':
                    printer(f'Update tyt')
                    update_pool = get_packages_changes(request.form.items())
                    # print(update_pool['install'])
                    # print(update_pool['delete'])
                    front_data, update_logs = update_server_packages(front_data, update_pool, ssh, target, username)
                    full_log += update_logs + "=" * 30 + "\n"
                    if not front_data['update_delete'][0] or not front_data['update_install'][0]:
                        text, cat = 'Warning! Read LOG carefully!', 'error'
                    else:
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
        'servers/warm_up.html', query=target, full_log=full_log, data=front_data, user=current_user, ver=ver)
