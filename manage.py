"""
Run database migrations and upgrades.

create a new database "test". Then,
In a terminal:


user@pc:~$ python manage.py db init


This will create a folder called migrations
This will add a migrations folder to your application.
with alembic.ini and env.py files
and a sub-folder migrations which will include
your future migrations. It has to be run only once.
The contents of this folder need to be added to version control
along with your other source files.


user@pc:~$ python manage.py db migrate


Generates a new migration in the migrations folder.
The file is pre-filled
based on the changes detected by alembic,
edit the description message at the beginning of the file
and make any change you want.


user@pc:~$ python manage.py db upgrade


Implements the changes in the migration files
in the database and updates the version of the migration
in the alembic_version table.
"""
from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_app import app
from flask_app import db

migrate = Migrate(app,db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()