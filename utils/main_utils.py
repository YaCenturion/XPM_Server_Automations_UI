# -*- coding: utf-8 -*-
import os
from datetime import datetime
from ..models import *
# from db_preset import create_db_and_update_data  # All for a clear start. Need to kill previous DB.


def get_like(way, search_query):
    query = f"%{search_query}%"
    if way == 'companies':
        res = Companies.query.filter(
                (Companies.name.ilike(query)) |
                (Companies.full_name.ilike(query)) |
                (Companies.id.ilike(query)) |
                (Companies.comments.ilike(query))
                ).all()
        print(res)
    elif way == 'persons':
        res = Persons.query.filter(
                (Persons.name.ilike(query)) |
                (Persons.id.ilike(query)) |
                (Persons.phone.ilike(query)) |
                (Persons.comments.ilike(query))
                ).all()
        print(res)
    else:
        res = False

    if not res:
        res = 0
    return res


def save_in_db(item):
    try:
        db.session.add(item)
        db.session.commit()
        result = True
    except Exception as e:
        printer(f'Error IN: save_in_db, MSG: {e}')
        result = False
    return result


def get_endpoint(text):
    return str(text).replace('_', ' ').capitalize()


def show_post_data(form_data):
    for key, value in form_data:
        print(f"{key}: {value}")


def company_exists(name, full_name):
    return Companies.query.filter_by(name=name, full_name=full_name).first() is not None


def contract_exists(num_index):
    return Contracts.query.filter_by(num_index=num_index).first() is not None


def domain_exists(name):
    return Contracts.query.filter_by(name=name).first() is not None


def person_exists(name):
    return Persons.query.filter_by(name=name).first() is not None


def get_all_companies():
    return [(company.id, company.name) for company in Companies.query.all()]


def get_all_contracts():
    return [(contract.id, str(contract.id)) for contract in Contracts.query.all()]


def get_all_hostings():
    return [(hosting.id, str(hosting.id)) for hosting in Hostings.query.all()]


def get_all_domains():
    return [(domain.id, str(domain.id)) for domain in Domains.query.all()]


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


# def get_timestamp_to_date(timestamp, view):
#     if timestamp is None:
#         return None
#     if view == '%d.%m.%Y':
#         normal_date = datetime.fromtimestamp(timestamp)
#         return normal_date.strftime('%d.%m.%Y')
#     elif view == '%Y-%m-%d':
#         dt_object = datetime.utcfromtimestamp(timestamp)
#         return dt_object.strftime('%Y-%m-%d')
#     else:
#         return None


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


def send_command(ssh, string):
    stdin, stdout, stderr = ssh.exec_command(string)
    result = stdout.read().decode('utf-8')
    return result
