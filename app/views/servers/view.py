from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required  # login_user, logout_user
# from sqlalchemy import desc  # func
from app import ver
from config import ansible_host, playbooks_lst
from app.utils.main_utils import *
# from app import client_pay_status_lst

servers = Blueprint('servers', __name__)


@login_required
@servers.route('/warm_up/', methods=['GET', 'POST'])
def warm_up():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    front_data, query = {}, False
    if request.method == 'POST':
        printer(f'Get POST data from: /{request.endpoint}', current_user.username)
        show_post_data(request.form.items())

        query = str(request.form['ip_address']).strip()

        ssh, msg = get_ssh(ansible_host)
        if ssh:
            command = f'ansible-playbook /etc/ansible/{playbooks_lst["get_facts"]} -i {query}, -e "target={query}"'
            status, log = exec_ansible_playbook(ssh, command, current_user.username)

            if status:
                front_data = {'report': [True, log]}
            else:
                front_data = {'report': [False, log]}
        else:
            front_data = {'report': [False, msg]}
        if not front_data['report'][0]:
            text = 'Warning! Read LOG carefully!'
            cat = 'error'
            flash(text, cat)

    return render_template('servers/warm_up.html', query=query, data=front_data, user=current_user, ver=ver)
