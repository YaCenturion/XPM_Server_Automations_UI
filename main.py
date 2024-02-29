#!/usr/bin/env python

# from flask_migrate import Migrate, MigrateCommand
# from flask_script import Manager, Shell, Server
from app import create_app, db
from app.models import Users
from config import *


# @manager.command
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


def run_shell():
    def make_shell_context():
        return dict(app=app, db=db, Users=Users, Role=user_app_role_lst)

    # manager.add_command('shell', Shell(make_context=make_shell_context))
    # manager.add_command('db', MigrateCommand)
    # manager.add_command('runserver', Server(host="0.0.0.0"))


def starter():
    with app.app_context():
        if cfg['from_zero']:
            db.drop_all()
            db.create_all()
            db.session.commit()
        if cfg['from_zero']:
            from db_presets import create_db_and_update_data
            create_db_and_update_data(app)
        if cfg['fake_data']:
            Users.generate_fake(count=cfg['fake_data'])


app = create_app()

# manager = Manager(app)
starter()
# migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run()
