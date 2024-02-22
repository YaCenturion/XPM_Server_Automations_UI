# Roles templates for generate playbooks
base_pattern = [
    {
        "name": None,
        "hosts": "{{ target }}",
        "remote_user": "xpmans",
        "become": "yes",
        "vars": {
            "state_action": "{{ state_action | default('___NOT_SET___') }}"
        },
        "roles": []
    }
]

r_system = {
    'user': {'role': 'create_linux_user', 'vars': {'state_action': None}},  # absent|present
    'directory': {'role': 'create_user_directory', 'vars': {'state_action': None}},  # absent|directory

    'install_mysql_module': {'role': 'install_mysql_module'},
}
r_db = {
    'db': {'role': 'create_db', 'vars': {'state_action': None}},  # absent|present
    'user': {'role': 'create_db_user', 'vars': {'state_action': None}},  # absent|present
}
r_web = {
    'create_php_fpm_sock': {'role': 'create_php_fpm_sock'},
    'SSL_certificate': {'role': 'create_self-signed_certificate'},
    'create_apache_virtualhost': {'role': 'create_apache_virtualhost'},
    'ftp_user': {'role': 'create_ftp_user'},
    'restart_apache': {'role': 'restart_apache'},
}
