from app.models import *
# import app.app_context


def create_db_and_update_data(app):  # For create DB and fill tables
    with app.app_context():
        db.create_all()

        def add_to_db(pool):
            for unit in pool:
                db.session.add(unit)

        add_list = [
            # Creating users
            root_user, user1,
        ]
        add_to_db(add_list)
        # Commit
        db.session.commit()
        print('DB created & updated from preset all data\n')


# ######################################### Default Users
root_user = Users(
    username='root',  # type: ignore[call-arg]
    name='Darth Vader',  # type: ignore[call-arg]
    email='boris.drozdovsky@gmail.com',  # type: ignore[call-arg]
    password_hash=generate_password_hash('xriT8o]xZ7549E2'),  # type: ignore[call-arg]
    app_role=0,  # type: ignore[call-arg]
    create=1685782415,  # type: ignore[call-arg]
    reserved=None  # type: ignore[call-arg]
)

user1 = Users(
    username='boris',  # type: ignore[call-arg]
    name='Boris Drozdovski',  # type: ignore[call-arg]
    email='boris.d@expim.co.il',  # type: ignore[call-arg]
    password_hash=generate_password_hash('xriT8o]xZ7549E2'),  # type: ignore[call-arg]
    app_role=1,  # type: ignore[call-arg]
    create=1685782415,  # type: ignore[call-arg]
    reserved=None  # type: ignore[call-arg]
    )
