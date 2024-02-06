from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from password_strength import PasswordPolicy
from app.models import *
from config import *


policy = PasswordPolicy.from_names(length=6, uppercase=1, numbers=1, special=1)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class AddUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Login', validators=[DataRequired()])
    app_role = SelectField('Access level', choices=user_app_role_lst, validators=[DataRequired()])
    email = StringField('Work e-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add new user')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a unique username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a unique email address.')

    def validate_password(self, password):
        if policy.test(password.data):
            raise ValidationError(
                "The password is not complex enough, it should contain at least: "
                "1 lowercase letter, 1 uppercase letter , 1 symbol and 1 number")


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class AddContractForm(FlaskForm):
    company_id = SelectField('Companies ID', coerce=int, validators=[DataRequired()])
    pay_per_month = IntegerField('Pay per month', validators=[DataRequired()])
    start_date = IntegerField('Start Date', validators=[DataRequired()])
    end_date = IntegerField('End Date', validators=[DataRequired()])
    # TODO заменить - чтобы было про каждый месяц
    num_all_acts = StringField('Number of All Acts', validators=[DataRequired()])
    close_acts = StringField('Close Acts', validators=[DataRequired()])
    submit = SubmitField('Add new contract')


class AddDomainsForm(FlaskForm):
    company_id = SelectField('Companies ID', coerce=int, validators=[DataRequired()])
    contracts_id = SelectField('Contracts ID', coerce=int, validators=[DataRequired()])
    hostings_id = SelectField('Hostings ID', coerce=int, validators=[DataRequired()])
    subdomain = BooleanField('Subdomain')
    url = StringField('URL', validators=[DataRequired()])
    alias = StringField('Alias', validators=[DataRequired()])
    created_at = IntegerField('Created At', validators=[DataRequired()])
    next_pay_date = IntegerField('Next Pay Date', validators=[DataRequired()])
    https_enabled = BooleanField('HTTPS Enabled')
    https_payment = IntegerField('HTTPS Payment')
    registrar = StringField('Registrar', validators=[DataRequired()])
    panel_address = StringField('Panel Address', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])


class AddHostingsForm(FlaskForm):
    company_id = SelectField('Companies ID', coerce=int, validators=[DataRequired()])
    company_name = StringField('Companies Name', validators=[DataRequired()])
    panel_address = StringField('Panel Address', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    paid_until = IntegerField('Paid Until', validators=[DataRequired()])
    plan_name = StringField('Plan Name', validators=[DataRequired()])
    ip_address = StringField('IP Address', validators=[DataRequired()])
    server_name = StringField('Server Name', validators=[DataRequired()])
    ssh_keys = TextAreaField('SSH Keys')


class AddSitesDataForm(FlaskForm):
    company_id = SelectField('Companies ID', coerce=int, validators=[DataRequired()])
    domains_id = SelectField('Domains ID', coerce=int, validators=[DataRequired()])
    cms_name = StringField('CMS Name', validators=[DataRequired()])
    cms_base_version = StringField('CMS Base Version', validators=[DataRequired()])
    panel_address = StringField('Panel Address', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    bootstrap_version = StringField('Bootstrap Version', validators=[DataRequired()])
    fontawesome_version = StringField('Font Awesome Version', validators=[DataRequired()])
    uses_modules = StringField('Uses Modules', validators=[DataRequired()])
    handmade_scripts = TextAreaField('Handmade Scripts')


class AddMailSystemsForm(FlaskForm):
    company_id = SelectField('Companies ID', coerce=int, validators=[DataRequired()])
    domains_id = SelectField('Domains ID', coerce=int, validators=[DataRequired()])
    mail_system = StringField('Mail System', validators=[DataRequired()])
    control_panel = StringField('Control Panel', validators=[DataRequired()])
    admin_login = StringField('Admin Login', validators=[DataRequired()])
    admin_password = StringField('Admin Password', validators=[DataRequired()])
    mailboxes = TextAreaField('Mailboxes')


class AddIdentifiersForm(FlaskForm):
    domains_id = SelectField('Domains ID', coerce=int, validators=[DataRequired()])
    ya_acc_metrika = StringField('Yandex.Metrika Account', validators=[DataRequired()])
    g_acc_analytics = StringField('Google Analytics Account', validators=[DataRequired()])
    g_webmaster = StringField('Google Webmaster Tools', validators=[DataRequired()])
    ya_webmaster = StringField('Yandex Webmaster Tools', validators=[DataRequired()])
