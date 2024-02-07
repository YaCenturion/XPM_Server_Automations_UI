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
    host = False
    front_data = {}
    full_log = ""
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', current_user.username)
        show_post_data(request.form.items())

        host = str(request.form['ip_address']).strip()
        ssh, msg = get_ssh(ansible_host)

        if ssh:
            full_log = "=" * 30 + "\n"
            # Ansible: Update packages
            if 'update' in request.form:
                if request.form['update'] == 'true':
                    printer(f'Update tyt')
                    remove_pool, install_pool = [], []
                    for key, value in request.form.items():
                        if value == '+set':
                            install_pool.append(key)
                        elif value == '-del':
                            remove_pool.append(key)

                    printer(install_pool)
                    printer(remove_pool)

                    # if len(remove_pool) > 0:
                    #     command = f'{playbooks_lst["base"]}{playbooks_lst["remover"]} -i {host}, -e "target={host}"'
                    #     status_update, ssh_log = exec_ansible_playbook(ssh, command, current_user.username)
                    #     full_log += ssh_log
                    #     front_data['update_rm'] = [status_update, ssh_log]
                    # elif len(install_pool) > 0:
                    #     command = f'{playbooks_lst["base"]}{playbooks_lst["installer"]} -i {host}, -e "target={host}"'
                    #     status_update, ssh_log = exec_ansible_playbook(ssh, command, current_user.username)
                    #     full_log += ssh_log
                    #     front_data['update_set'] = [status_update, ssh_log]

            # Ansible: Get facts
            command = f'{playbooks_lst["base"]}{playbooks_lst["get_facts"]} -i {host}, -e "target={host}"'
            status_get_facts, ssh_log = exec_ansible_playbook(ssh, command, current_user.username)
            full_log += ssh_log

            if status_get_facts:
                result, data_pool = handler_facts(ssh_log)
                if result:
                    front_data['get_facts'] = [result, ssh_log]
                    front_data['packages'] = data_pool

            front_data['get_facts'] = [status_get_facts, ssh_log]
            close_ssh(ssh, current_user.username)
        else:
            front_data['get_facts'] = [False, msg]

        if not front_data['get_facts'][0]:
            text = 'Warning! Read LOG carefully!'
            cat = 'error'
            flash(text, cat)

    return render_template('servers/warm_up.html', query=host, full_log=full_log, data=front_data, user=current_user, ver=ver)
