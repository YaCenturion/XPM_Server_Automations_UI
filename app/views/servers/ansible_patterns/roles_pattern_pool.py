# Roles templates for generate playbooks
base_pb_pattern = [
    {
        "name": None,
        "hosts": None,
        "remote_user": None,
        "become": None,
        "vars": {},
        "roles": [],
    }
]

roles = {
    'system': {
        'user': {'role': 'create_linux_user'},  # absent|present
        'directory': {'role': 'create_user_directory'},  # absent|directory
        'ssl_directory': {'role': 'create_ssl_directory'},  # absent|directory
        'install_mysql_module': {'role': 'install_mysql_module'},
    },
    'db': {
        'db': {'role': 'create_db'},  # absent|present
        'user': {'role': 'create_db_user'},  # absent|present
    },
    'web': {
        'create_php_fpm_sock': {'role': 'create_php_fpm_sock'},
        'SSL_certificate': {'role': 'create_self-signed_certificate'},
        'create_apache_virtualhost': {'role': 'create_apache_virtualhost'},
        'create_nginx_virtualhost': {'role': 'create_nginx_virtualhost'},
        'ftp_user': {'role': 'create_ftp_user'},
        'restart_apache': {'role': 'restart_apache'},
    },
}


# Defs with presets for generate list of roles action:
def add_new_virtualhost(web_server):
    return [
        (roles['system']['user'],),
        (roles['system']['directory'],),
        (roles['system']['ssl_directory'],),
        (roles['system']['install_mysql_module'],),
        (roles['db']['db'],),
        (roles['db']['user'],),
        (roles['web']['create_php_fpm_sock'],),
        (roles['web']['SSL_certificate'],),
        (roles['web'][f'create_{web_server}_virtualhost'],),
        (roles['web']['ftp_user'],),
        (roles['web'][f'restart_{web_server}'],),
    ]
