from app import db, login
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


from app import db, login


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100))
    email = db.Column(db.String(100),index=True, unique=True)
    email1 = db.Column(db.String(100),index=True, unique=True)
    password_hash=db.Column(db.String(128))

    def __repr__(self):
        return f'Пользователь {description}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return(check_password_hash(self.password_hash, password))



class Clinics(db.Model):
    __tablename__ = 'Clinics'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100))
    robots = db.relationship('Robots',backref='clinics',lazy='dynamic')
    patient = db.relationship('Patients',backref='clinics',lazy='dynamic')

    def __repr__(self):
        return f'Клиника {self.description}'

class Robots(db.Model):
    __tablename__ = 'Robots'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinics.id'))
    description = db.Column(db.String(100))

    def __repr__(self):
        return f'Робот {self.description}'

class Patients(db.Model):
    __tablename__ = 'Patients'
    id = db.Column(db.Integer(), primary_key=True)
    snils_hash =db.Column(db.String(128))
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinics.id'))
    patient_snils = db.Column(db.String(11))
    #fio = db.Column(db.String(100))
    birthdate = db.Column(db.Date())
    sex = db.Column(db.String(1))

    def __repr__(self):
        return f'Пациент {self.snils}'

    def get_snils_hash(self, snils):
        digest = md5(snils.lower().encode('utf-8')).hexdigest()
        self.snils_hash = digest
