from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required  # login_user, logout_user
from sqlalchemy import desc  # func
from app import ver
# from app.email import send_email
# from app.models import *
from app.forms.forms import AddUserForm, ChangePasswordForm
from app.utils.main_utils import *

users = Blueprint('users', __name__)


@users.route('/all/')
@login_required
def all_users():
    if not current_user.is_authenticated:
        return redirect(url_for('general.login'))
    if current_user.app_role in (0, 1):
        all_users_pool = Users.query.order_by(desc(Users.active))
        return render_template("users/all.html", users=all_users_pool, user=current_user, ver=ver)
    else:
        return abort(401)


@users.route('/add/', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.app_role not in (0, 1):
        return abort(401)
    web_form = AddUserForm()

    if web_form.validate_on_submit():
        user = Users(
            name=web_form.name.data,  # type: ignore[call-arg]
            username=web_form.username.data,  # type: ignore[call-arg]
            email=web_form.email.data,  # type: ignore[call-arg]
            app_role=web_form.app_role.data,  # type: ignore[call-arg]
        )
        user.set_password(web_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Created successfully!', 'success')
        return redirect(url_for('index'))
    if request.method == 'POST':
        flash('Attention!', 'error')
        get_form_errors(web_form)
    return render_template(
        'users/add.html', form=web_form, creator=current_user.app_role, user=current_user, ver=ver)


@users.route('/change-password/<int:num_id>', methods=['GET', 'POST'])
@login_required
def change_user_password(num_id):
    web_form = ChangePasswordForm()
    user = Users.query.get_or_404(num_id)
    if web_form.validate_on_submit():
        user.set_password(web_form.password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('account.all_users'))
    if request.method == 'POST':
        flash('Attention!', 'error')
        get_form_errors(web_form)
    return render_template('users/change_password.html', form=web_form, user=current_user, ver=ver)
