# -*- coding: utf-8 -*-
import os
import re
import paramiko
import pymssql
import random
import string
# import json
import yaml
import socket
# from datetime import datetime
from ..models import *


def save_in_db(item):
    try:
        db.session.add(item)
        db.session.commit()
        result = item
    except Exception as e:
        printer(f'Error IN: save_in_db, MSG: {e}')
        result = False
    return result


def get_endpoint(text):
    return str(text).replace('_', ' ').capitalize()


def show_post_data(form_data):
    for key, value in form_data:
        print(f"{key}: {value}")


# def db_warm_up(app, db_name):
#     if not check_file_exists(db_name):
#         create_db_and_update_data(app)  # Create data
#     else:
#         with app.app_context():
#             db.create_all()
#         print('Not need create DB from zero.')


def check_file_exists(filename, directory='instance'):
    file_path = os.path.join(directory, filename)
    print('DB status:', os.path.isfile(file_path))
    return os.path.isfile(file_path)


def get_timestamp(date_string):
    timestamp = datetime.strptime(date_string, '%Y-%m-%d').timestamp()
    return int(timestamp)


def get_form_errors(form):
    # Действия, если форма не прошла валидацию
    for field, errors in form.errors.items():
        for error in errors:
            print(f"Error in field '{getattr(form, field).label.text}': {error}")


def delete_files(path='static/report', n=5):
    files = os.listdir(path)
    if len(files) <= n:
        printer(f':: In directory: "{path}" not many files')
        return

    files = [os.path.join(path, f) for f in files]
    files = sorted(files, key=os.path.getmtime)

    while len(files) > n:
        oldest_file = files[0]
        if not oldest_file.endswith(('.html', '.me')) and os.path.isfile(oldest_file):
            os.remove(oldest_file)
        files = files[1:]
    printer(f':: Delete old files in directory: "{path}". Now less than {n} files')


def printer(text, user='N/A'):
    log_directory = "logs"
    log_file = os.path.join(log_directory, "latest.log")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    if os.path.exists(log_file) and os.path.getsize(log_file) > 200000:  # Проверяем размер файла логов
        backup_name = time.strftime("logs/backup-%Y%m%d-%H%M%S.log")
        os.rename(log_file, backup_name)
        with open(log_file, "w", encoding='utf-8') as f:  # Очищаем файл логов
            f.write("")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding='utf-8') as f:  # Дописываем текст в файл логов
        f.write(f"[{current_time}] User: {user} - {text}\n")

    print(text)
    return text


def get_ssh(cred):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = cred['host']
    port = cred['port']
    user = cred['user']
    key_path = cred['key_path']
    try:
        ssh.connect(host, port, user, key_filename=key_path, timeout=2, allow_agent=False, look_for_keys=False)
        msg = printer(f':: ANSIBLE_SRV Authentication - OK!')
    except paramiko.AuthenticationException as e:
        ssh = False
        msg = printer(f'-- SSH Authentication to ANSIBLE_SRV - ERROR: {e}')
    except paramiko.SSHException as e:
        ssh = False
        msg = printer(f'-- SSH Connection to ANSIBLE_SRV - ERROR: {e}')
    except socket.timeout as e:
        ssh = False
        msg = printer(f'-- Connection to ANSIBLE_SRV timed out: {e}')
    except Exception as e:
        ssh = False
        msg = printer(f'-- An unexpected error occurred: {e}')
    return ssh, msg


def get_ansible_inventory(ssh, output):
    stdin, stdout, stderr = ssh.exec_command(f'ansible-inventory --{output} --list')
    if stderr:
        printer(f'ERROR GET Inventory from ANSIBLE_SRV: {stderr.read()}')
    result = stdout.read().decode('utf-8')
    return result


def deploy_updated_inventory(ssh, inventory_dict, inventory_ini, ui_user):
    # Backup inventory_ui
    command = 'cp -f /etc/ansible/hosts/inventory_ui.* /etc/ansible/hosts-backups/'
    exec_ssh_command(ssh, command, ui_user)

    # Save updated inventory_ui
    file = '/etc/ansible/hosts/inventory_ui'
    with ssh.open_sftp() as sftp:
        with sftp.file(f'{file}.yaml', 'w') as f_yaml:
            yaml.dump(inventory_dict, f_yaml, default_flow_style=False)
        with sftp.file(f'not_in_use_copy.ini', 'w') as f_ini:
            f_ini.write(inventory_ini)


def exec_ansible_playbook(ssh, command, ui_user):
    result = True
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        msg = printer(f":::: Executed Ansible:\n:::: {command}\n", ui_user)
    except Exception as ex:
        msg = printer(f"---- Error executing playbook: {ex}")
        return False, msg
    out = str(stdout.read().decode('utf-8'))
    err = str(stdout.read().decode('utf-8'))

    if 'unreachable=0' in out and 'failed=0' in out:
        block_name = ":::: Execution result SUCCESS"
    else:
        result = False
        block_name = "---- Execution result WARNING"
    msg += printer(f"{block_name}:\n{out}\n{err}\n")

    if "SUCCESS" in block_name:
        msg += '\n:::: Ansible playbook execute success.\n'
    else:
        msg += '\n---- Read the LOG! Somthing looks not good.\n'

    return result, msg


def exec_ssh_command(ssh, command, ui_user):
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        msg = printer(f":::: Executed SSH command:\n:::: {command}\n", ui_user)
    except Exception as ex:
        msg = printer(f"---- Error executing playbook: {ex}")
        return False, msg
    out = str(stdout.read().decode('utf-8')).strip()
    err = str(stdout.read().decode('utf-8')).strip()

    block_name = ":::: Execution result SUCCESS"
    if out or err:
        block_name += f"\nOutput: {out}\nError: {err}\n"
    msg += printer(f"{block_name}")

    if not err:
        msg += '\n:::: Execute command success.\n'
    else:
        msg += '\n---- Read the LOG! Somthing looks not good.\n'
        return False, msg
    return True, msg


def close_ssh(ssh, user):
    ssh.close()
    printer(':: SSH Connection close\n', user)
    return


def generate_password(length):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def get_priority_detailed_info(cred, company_id):
    company_id = "(" + company_id + ")"
    query = f"""
        SELECT DOCUMENTS.DOC, DOCUMENTS.DOCNO, DOCUMENTS.CUST, CUSTOMERS.CUSTNAME, CUSTOMERS.CUSTDES,
            SERVCONT.PHONE, SERVCONTITEMS.CONTI, SERVCONTITEMS.CONT, SERVCONTITEMS.PART, PART.PARTNAME
        FROM PART
            INNER JOIN SERVCONTITEMS ON PART.PART = SERVCONTITEMS.PART
            INNER JOIN DOCUMENTS ON DOCUMENTS.DOC = SERVCONTITEMS.CONT
            INNER JOIN CUSTOMERS ON DOCUMENTS.CUST = CUSTOMERS.CUST
            INNER JOIN SERVCONT ON DOCUMENTS.DOC = SERVCONT.DOC
        WHERE SERVCONT.CONTSTATUS = 3
            AND CUSTOMERS.RESTRICTED <> N'Y'
            AND CUSTOMERS.CUSTNAME in {company_id} 
        ORDER BY DOCUMENTS.DOC, CUSTOMERS.CUSTNAME, DOCUMENTS.DOCNO;
    """

    rows = priority_query(cred, query, company_id)
    return rows


def priority_query(cred, query, args=False):
    conn, cursor = get_connect_priority_mssql(cred)
    if args:
        cursor.execute(query, (args,))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_connect_priority_mssql(cred):  # Connect to the MSSQL database
    conn = pymssql.connect(
        host=cred['DB_host_int'], user=cred['DB_user'], password=cred['DB_password'], database=cred['DB_name']
    )
    cursor = conn.cursor()
    return conn, cursor


def clear_table(table_name):
    rows = len(table_name.query.all())
    print(f'Table {table_name} contains {rows}')
    while rows > 0:
        db.session.query(table_name).delete()
        db.session.commit()
        time.sleep(1)
        rows = len(table_name.query.all())
    print(f'Table {table_name} truncated and contains {rows}')
    return True


def save_inventory_local(filename_inv, inventory, inventory_ini):
    with open(f'{filename_inv}_updated.yaml', 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)
    with open(f'{filename_inv}_updated.ini', 'w') as file:
        file.write(inventory_ini)


def get_php_fpm_installed(php_fpm_versions):
    php_fpm_lst = []
    if isinstance(php_fpm_versions, list) and len(php_fpm_versions) > 0:
        for version in php_fpm_versions:
            if 'php' in str(version):
                for i in ('php', 'fpm', '-', '.'):  # D:php8.0-fpm , RH:php80-php-fpm
                    version = str(version).replace(i, '')
                if len(version) == 2:
                    dot_version = f"{version[0]}.{version[1]}"
                    php_fpm_lst.append((dot_version, dot_version, version, f'PHP-FPM {dot_version}'))
        return php_fpm_lst
    return False


def get_php_fpm_path(php_fpm_services):  # D:php8.0-fpm.service  Rh:php81-php-fpm.service
    def digits_inside(item):
        return bool(re.search(r'\d', item))

    if len(php_fpm_services) == 1:
        for row in php_fpm_services:
            if not digits_inside(row):
                return True
    return False
