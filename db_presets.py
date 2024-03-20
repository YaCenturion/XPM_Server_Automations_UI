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
            r_user
        ]

        for row in ui_users:
            usr = Users(
                username=row[0],  # type: ignore[call-arg]
                name=row[1],  # type: ignore[call-arg]
                email=row[2],  # type: ignore[call-arg]
                password_hash=generate_password_hash(row[3]),  # type: ignore[call-arg]
                app_role=row[4],  # type: ignore[call-arg]
                create=1685782415,  # type: ignore[call-arg]
                reserved=None  # type: ignore[call-arg]
            )
            add_list.append(usr)

        add_to_db(add_list)

        # Commit
        db.session.commit()
        print('DB created & updated from preset all data\n')


# ######################################### Default Users
r_user = Users(
    username='root',  # type: ignore[call-arg]
    name='D. Vader',  # type: ignore[call-arg]
    email='boris.drozdovsky@gmail.com',  # type: ignore[call-arg]
    password_hash=generate_password_hash('xriT8o]xZ7549E2'),  # type: ignore[call-arg]
    app_role=0,  # type: ignore[call-arg]
    create=1685782415,  # type: ignore[call-arg]
    reserved=None  # type: ignore[call-arg]
)

ui_users = [
    # (login, name, e-mal, pw, role)
    ('boris', 'Boris Drozdovski', 'boris.d@expim.co.il', 'xriT8o]xZ7549E2', 1),
    ('liron', 'Liron Hadad', 'liron@expim.co.il', '4P9pVn#uyAscxwwF', 1),
    ('ofir', 'Ofir Hadad', 'ofir@expim.co.il', 'MasterOfUniverse', 1),

    ('amit.z', 'Amit Zertal', 'amit.z@expim.co.il', '9.DE9v>FdaP=nn', 2),
    ('david.b', 'David Binaev', 'david.b@expim.co.il', 'RC@X9x1L_4_W>=', 2),
    ('david.s', 'David Sasson', 'david.s@expim.co.il', 'Ma3q3@d;X+;hbF', 2),
    ('haim.m', 'Haim Malkukian', 'haim.m@expim.co.il', 'DX12.uB!CwY;m@', 2),
    ('rafaela.g', 'Rafaela Garnaga', 'rafaela.g@expim.co.il', 'Ra060365!', 2),
    ('ran.k', 'Ran Kantor', 'ran.k@expim.co.il', 'y6T_1FWmiwbR)g', 2),
    ('shaked.l', 'Shaked Levi', 'shaked.l@expim.co.il', '5~mE6HV3RcsdtE', 2),
    ('michal.g', 'Michal Gelman', 'michal.g@expim.co.il', 'v9G)xTFUGRBxfs', 2),
]
