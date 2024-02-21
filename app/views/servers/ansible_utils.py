
def generate_role_line(role, vars_pool=None):  # gen role line
    res = {'role': role}
    if not vars_pool or vars_pool is not None:
        res['vars'] = {}
        for item in vars_pool:
            if "directory" in role and item[0] == 'state_action' and item[1] == 'present':
                item[1] = "directory"
            res['vars'] = {
                item[0]: item[1]
            }
    return res


def generate_playbook(pattern_name, pb_name, roles_block):
    with open(f'ansible_patterns/{pattern_name}.yml', 'r') as pattern_file:
        rows_list = pattern_file.readlines()
        # print(rows_list[0])
        print(type(rows_list))
        rows_list[0] = rows_list[0].strip().replace('- name: NoName', f'- name: {pb_name}\n')
        print()
        print(rows_list[0])
        print()
        for role in roles_block:
            role_line = f'    - {role}\n'
            rows_list.append(role_line)

    return rows_list


def save_playbook(ssh, filename, rows_list):
    print(ssh)
    with open(f'ansible_patterns/{filename}.yml', 'w') as output_file:
        for row in rows_list:
            output_file.write(row)
    print('Done')


if __name__ == '__main__':
    pool = [
        ('create_linux_user', [['state_action', "present"], ['foo_action', "present"]]),
        ('create_user_directory', [['state_action', "present"]]),
        ('install_mysql_module', []),
        ('create_db', [['state_action', "present"]]),
        ('create_db_user', [['state_action', "present"]]),
        ('create_php_fpm_sock', []),
        ('create_self-signed_certificate', []),
        ('create_apache_virtualhost', []),
        ('create_ftp_user', []),
        ('restart_apache', []),
    ]
    roles = []
    for task in pool:
        roles.append(generate_role_line(task[0], task[1]))

    print(roles)
    result = generate_playbook('setup_new_web', 'THIS IS NAME', roles)
    save_playbook('will be ssh', 'new_filename', result)
