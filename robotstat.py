import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import Clinics, Robots, Patients, Users

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Robots=Robots, Clinics=Clinics, Patients=Patients, Users=Users)

#if __name__ == '__main__':
#    app.run(debug=True)
