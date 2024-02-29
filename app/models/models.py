# from flask import current_app
import time
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, login


@login.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    app_role = db.Column(db.Integer, default=3)  # Root: 0, Office: 1, Ops: 2
    create = db.Column(db.Integer, default=int(time.time()))
    reserved = db.Column(db.String(300), default=None)

    def __repr__(self):
        return f'<User {self.username}>'

    def full_name(self):
        return '%s %s' % (self.username, self.name)

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_fake(count=20, **kwargs):  # Generate a number of fake users for testing
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker

        fake = Faker()

        seed()
        for i in range(count):
            fake_u = Users(
                username=fake.user_name(),  # type: ignore[call-arg]
                name=fake.name(),  # type: ignore[call-arg]
                email=fake.email(),  # type: ignore[call-arg]
                password_hash=generate_password_hash('pAssWord'),  # type: ignore[call-arg]
                app_role=choice([1, 2, 3]),  # type: ignore[call-arg]
                create=1725782415,  # type: ignore[call-arg]
                reserved=None,  # type: ignore[call-arg]
                # password='pAssWord',
                **kwargs)  # type: ignore[call-arg]
            db.session.add(fake_u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class TasksHistory(db.Model):
    __tablename__ = 'tasks_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    host = db.Column(db.String(30))  # ip address
    status = db.Column(db.Boolean, default=False)  # 0: error, 1: success
    exec_time = db.Column(db.Integer)
    exec_filename = db.Column(db.String(255))  # playbook filename
    exec_command = db.Column(db.String(255))  # exec command
    exec_title = db.Column(db.String(255))  # playbook title
    exec_code = db.Column(db.Text)  # yaml text
    exec_log = db.Column(db.Text)  # console log
    comments = db.Column(db.Text)


class VirtualIps(db.Model):
    __tablename__ = 'virtual_ips'
    id = db.Column(db.Integer, primary_key=True)
    virtual_ip = db.Column(db.String(100))
    internal_ip = db.Column(db.String(100))
    name = db.Column(db.String(100))
    os_type = db.Column(db.String(100), default=False)
    login = db.Column(db.String(100), default=False)
    marker = db.Column(db.String(100), default=False)
    ws_type = db.Column(db.String(100), default=False)
    confs_path = db.Column(db.String(300), default=False)
    ansible = db.Column(db.String(300), default=False)
    reserved = db.Column(db.String(300), default="NOT_USED")
    comment = db.Column(db.String(300))
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class NutanixVMs(db.Model):
    __tablename__ = 'nutanix_vms'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False)
    cluster_name = db.Column(db.String(255))
    vm_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    company_id = db.Column(db.Integer)
    contract_num = db.Column(db.String(255))
    num_vcpus_per_socket = db.Column(db.Integer)
    num_threads_per_core = db.Column(db.Integer)
    hardware_virtualization_enabled = db.Column(db.Boolean)
    num_sockets = db.Column(db.Integer)
    is_agent_vm = db.Column(db.Boolean)
    memory_size_mib = db.Column(db.Integer)
    # disk_list = db.Column(db.String(255))
    total_disks = db.Column(db.Integer)
    total_disks_size_mib = db.Column(db.Integer)
    gpu_list = db.Column(db.String(255))
    internal_ip = db.Column(db.String(255))
    subnet_reference = db.Column(db.String(255))
    power_state = db.Column(db.Boolean)
    machine_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<Nutanix VM: {self.vm_name}>"


class NutanixDetails(db.Model):
    __tablename__ = 'nutanix_details'
    id = db.Column(db.Integer, primary_key=True)
    CUSTOMERS_CUSTNAME = db.Column(db.String(255))
    DOCUMENTS_DOC = db.Column(db.Integer)
    DOCUMENTS_DOCNO = db.Column(db.String(255))
    PART_PARTNAME = db.Column(db.String(255))

    def __repr__(self):
        return f"<Nutanix details: {self.DOCUMENTS_DOCNO} - {self.PART_PARTNAME}>"


class PriorityCompanies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custname = db.Column(db.String(64))  # company_id
    cust = db.Column(db.Integer)
    address = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    custdes = db.Column(db.String(64))
    vatflag = db.Column(db.String(64))
    pay = db.Column(db.Integer)
    fax = db.Column(db.String(64))
    zip = db.Column(db.String(64))
    state = db.Column(db.String(64))
    monthly = db.Column(db.String(64))
    account = db.Column(db.Integer)
    ivtype = db.Column(db.String(64))
    country = db.Column(db.Integer)
    restricted = db.Column(db.String(64))
    restrictdate = db.Column(db.Integer)
    statea = db.Column(db.String(64))
    createddate = db.Column(db.Integer)
    tivcontact = db.Column(db.Integer)
    edocuments = db.Column(db.String(64))
    nonprofitorg = db.Column(db.String(64))
