# Roles templates for generate playbooks
base_pattern = [
    {
        "name": None,
        "hosts": None,
        "remote_user": None,
        "become": None,
        "vars": {},
        "roles": [],
    }
]

r_system = {
    'user': {'role': 'create_linux_user'},  # absent|present
    'directory': {'role': 'create_user_directory'},  # absent|directory
    'ssl_directory': {'role': 'create_ssl_directory'},  # absent|directory

    'install_mysql_module': {'role': 'install_mysql_module'},
}
r_db = {
    'db': {'role': 'create_db'},  # absent|present
    'user': {'role': 'create_db_user'},  # absent|present
}
r_web = {
    'create_php_fpm_sock': {'role': 'create_php_fpm_sock'},
    'SSL_certificate': {'role': 'create_self-signed_certificate'},
    'create_apache_virtualhost': {'role': 'create_apache_virtualhost'},
    'ftp_user': {'role': 'create_ftp_user'},
    'restart_apache': {'role': 'restart_apache'},
}
