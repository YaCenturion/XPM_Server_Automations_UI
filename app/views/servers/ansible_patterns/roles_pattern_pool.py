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
        'injection_ansible_control': {'role': 'injection_ansible_control'},
        
        'user': {'role': 'create_linux_user'},  # absent|present
        'directory': {'role': 'create_user_directory'},  # absent|directory
        'ssl_directory': {'role': 'create_ssl_directory'},  # absent|directory
        'install_mysql_module': {'role': 'install_mysql_module'},
        
        'packages_action': {'role': 'packages_action'},
        'return_vhost_credentials': {'role': 'return_vhost_credentials'},
    },
    'db': {
        'db': {'role': 'create_db'},  # absent|present
        'user': {'role': 'create_db_user'},  # absent|present
        'mysql_secure_installation': {'role': 'mysql_secure_installation'},  # absent|present
        'mysql_cleaner': {'role': 'mysql_cleaner'},  # absent|present
    },
    'web': {
        'create_php_fpm_sock': {'role': 'create_php_fpm_sock'},
        'SSL_certificate': {'role': 'create_self-signed_certificate'},
        'create_apache_virtualhost': {'role': 'create_apache_virtualhost'},
        'create_nginx_virtualhost': {'role': 'create_nginx_virtualhost'},
        'ftp_user': {'role': 'create_ftp_user'},
        'restart_apache': {'role': 'restart_apache'},
        'restart_nginx': {'role': 'restart_nginx'},
        
        'apache_cleaner': {'role': 'apache_cleaner'},
        'apache_default_set': {'role': 'apache_default_set'},
        'nginx_cleaner': {'role': 'nginx_cleaner'},
        'nginx_default_set': {'role': 'nginx_default_set'},

        'create_reverse_proxy': {'role': 'create_reverse_proxy'},
    },
}


# Defs with presets for generate list of roles action:
def add_new_virtualhost(web_server):
    if web_server == 'reverse_proxy':
        roles_pool = [
            (roles['system']['user'],),
            (roles['system']['directory'],),
            (roles['system']['ssl_directory'],),
            (roles['system']['install_mysql_module'],),
            (roles['db']['db'],),
            (roles['db']['user'],),
            (roles['web']['create_php_fpm_sock'],),
            (roles['web']['SSL_certificate'],),
            (roles['web']['create_reverse_proxy'],),
            (roles['web']['ftp_user'],),
            (roles['web'][f'restart_nginx'],),
            (roles['web'][f'restart_apache'],),
            (roles['system'][f'return_vhost_credentials'],),
        ]
    else:
        roles_pool = [
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
            (roles['system'][f'return_vhost_credentials'],),
        ]
    return roles_pool


def injection_ansible_control():
    return [(roles['system']['injection_ansible_control'],),]


def packages_action(additional_role):
    if additional_role:
        return [
            (roles['system']['packages_action'],),
            (additional_role,),
                ]
    return [(roles['system']['packages_action'],),]
