from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app.app import create_app
from app.extensions import db
from app.models import Hint, Question, Task

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()