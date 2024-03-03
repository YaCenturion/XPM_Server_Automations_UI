from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
# from sqlalchemy import desc  # func
from app import ver
# from app.email import send_email
# from app.models import *
from urllib.parse import urlsplit
from app.forms.forms import *

general = Blueprint('general', __name__)


@login_required
@general.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('general.login'))
    return redirect(url_for(f'servers.server'))
    # if request.method == 'POST':
    #     if request.form['index_form'] == '1':
    #         search_query = request.form['global_search_string']
    #         print('query', search_query)
    #         # return render_template('index.html', user=current_user, ver=ver)
    #
    # return render_template('index.html', user=current_user, ver=ver)


@general.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('general.index'))
    web_form = LoginForm()
    if web_form.validate_on_submit():
        user = Users.query.filter_by(username=web_form.username.data).first()
        if user is None or not user.check_password(web_form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('general.login'))
        login_user(user, remember=web_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('general.index')
        flash('Welcome!', 'success')
        return redirect(next_page)
    return render_template('login.html', form=web_form, user=current_user, ver=ver)


@general.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logout now!', 'success')
    return redirect(url_for('general.index'))


@login_required
@general.route('/update_status/<subj>/<int:num_id>/<int:status>')
def update_status(subj, num_id, status):
    if current_user.app_role in (0, 1):
        if subj == 'user':
            back_page = url_for('users.all_users')
            unit = Users.query.get_or_404(num_id)
        # elif subj == 'company':
        #     back_page = url_for('companies.all_companies')
        #     unit = Companies.query.get_or_404(num_id)
        #     unit.active = status
        # elif subj == 'person':
        #     back_page = url_for('persons.all_persons')
        #     unit = Persons.query.get_or_404(num_id)
        # elif subj == 'domain':
        #     back_page = url_for('domains.all_domains')
        #     unit = Persons.query.get_or_404(num_id)
        # elif subj == 'hosting':
        #     back_page = url_for('hostings.all_hostings')
        #     unit = Persons.query.get_or_404(num_id)
        else:
            flash('Updated error!', 'error')
            back_page = url_for('general.index')
            unit = False

        if unit:
            unit.active = status
            db.session.commit()
    else:
        return abort(401)

    flash('Updated successfully!', 'success')
    return redirect(back_page)
