# from flask import current_app
import time
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


class ExecuteLogs(db.Model):
    __tablename__ = 'Execute_Logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip = db.Column(db.String(30))
    executed_at = db.Column(db.Integer, default=int(time.time()))
    status = db.Column(db.Boolean, default=True)  # 0: error, 1: success
    user_query = db.Column(db.String(255))
    console_log = db.Column(db.Text)
    comments = db.Column(db.Text)
