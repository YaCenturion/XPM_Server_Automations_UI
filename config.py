import os

cfg = {
    'sqlite_db_name': 'xpm_aui.db',
    'from_zero': False,  # True for clear DB TODO
    'fake_data': 0  # num rows for fake generator
}

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'Expim_Automations_UI')
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'uyTbf8AEtYjV3N6H48m6Z2vS3KjcEdXH'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')

    # Admin account
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'paS$w0rd')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'boris.drozdovski@gmail.com')
    EMAIL_SUBJECT_PREFIX = f'[{APP_NAME}]'
    EMAIL_SENDER = f'{APP_NAME} Admin <{MAIL_USERNAME}>'

    if os.environ.get('FLASK_ENV') == 'production':
        SSL_DISABLE = (os.environ.get('SSL_DISABLE', 'True') == 'True')

    @staticmethod
    def init_app(app):
        pass


user_app_role_lst = [
    ('0', 'Root'),
    ('1', 'Kings'),  # no limits
    ('2', 'OPs'),  # access only NOC menu
    ('20', 'OPs [read only]'),  # like NOC and only look
    ('3', 'Integration'),  # access only NOC menu
    ('30', 'Integration [read only]'),  # like NOC and only look
    ('4', 'Office'),  # access only Office menu
    ('40', 'Office [read only]'),  # like Office and only look
]

ansible_host = {
    'host': '172.16.5.6',
    'port': 22,
    'user': 'xpmadmin',
    'key_path': 'app/views/servers/ssh_keys/expim_ansible.pem',
}

fortigate = {
    'host': '172.16.100.1',  # IP Fortigate
    'token': '18mxw51txqG8p5GNt3r83rps3mgH0h',  # Token
    'url': 'https://172.16.100.1/api/v2/cmdb/firewall/vip',
}

nutanix = {
    'clusters_ip': ['172.16.16.40', '172.16.16.10', '172.16.16.60'],
    'cluster_username': 'tools-expim-api',
    'cluster_password': 'gj5098gHW4f3%',
}

playbooks_lst = {
    "base": 'ansible-playbook /etc/ansible/prod/',
    "show_me_yml": 'cat /etc/ansible/prod/',
    "prod_deploy": '/etc/ansible/prod/',
    "get_facts": 'get_facts.yml',
    "action": 'packages_action.yml',
    "apache_default": 'apache_default_conf.yml',
    "nginx_default": 'nginx_default_conf.yml',
    "apache_cleaner": 'apache_cleaner.yml',
    "nginx_cleaner": 'nginx_cleaner.yml',
}

linux_packages_dict = {
    'redhat': [  # label name, package_name, type
        # ['yum', 'yum', 'sys'],
        ['PHP 7.1 fpm', 'php71-fpm', 'web'],
        ['PHP 7.4 fpm', 'php74-php-fpm', 'web'],
        ['PHP 8.0', 'php80', 'web'],
        ['PHP 8.0 fpm', 'php80-php-fpm', 'web'],
        ['PHP 8.1', 'php81', 'web'],
        ['PHP 8.1 fpm', 'php81-php-fpm', 'web'],
        ['PHP 8.2 fpm', 'php82-php-fpm', 'web'],
        ['Memcached', 'memcached', 'other'],
        ['Pure-FTPd', 'pure-ftpd', 'web'],
        ['Python 2', 'python', 'other'],
        ['Python 3', 'python3', 'other'],
        ['Git', 'git', 'sys'],
        ['ElasticSearch', 'elasticsearch', 'other'],
        ['Zabbix Agent 2', 'zabbix-agent2', 'other'],
        ['Zip', 'zip', 'sys'],
        ['Tar', 'tar', 'sys'],
        ['OpenSSH', 'openssh', 'sys'],
        ['OpenLDAP', 'openldap', 'sys'],
        ['Nginx', 'nginx', 'web'],
        ['Apache 2', 'httpd', 'web'],
        ['MySQL Server', 'mysql-server', 'db'],
        ['MySQL Client', 'mysql-client', 'db'],
    ],
    'debian': [
        # ['apt', 'apt', 'sys'],
        ['Python 2', 'python', 'other'],
        ['Python 3', 'python3', 'other'],
        ['Zip', 'zip', 'sys'],
        ['Tar', 'tar', 'sys'],
        ['Git', 'git', 'sys'],
        ['Apache 2', 'apache2', 'web'],
        ['Nginx', 'nginx', 'web'],
        ['MySQL Server', 'mysql-server', 'db'],
        ['MySQL Client', 'mysql-client', 'db'],
        ['Varnish', 'varnish', 'other'],
        ['OpenSSH', 'openssh', 'sys'],
        ['OpenLDAP', 'openldap', 'sys'],
        ['Memcached', 'memcached', 'other'],
        ['Pure-FTPd', 'pure-ftpd', 'web'],
        ['ElasticSearch', 'elasticsearch', 'other'],
        ['Zabbix', 'zabbix-agent2', 'other'],
    ]
}
php_versions = [
    ('80', '80'),
    ('8.1', '8.1'),
    ('8.2', '8.2'),
    ('8.3', '8.3'),
    ('7.4', '7.4'),
]
