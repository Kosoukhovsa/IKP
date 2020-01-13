from app import db, login_manager
from flask import current_app
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from hashlib import md5
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import jwt
from time import time
from datetime import datetime


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

# Роли пользователей
class UserRoles(db.Model):
    __tablename__= 'UserRoles'
    id = db.Column(db.Integer(), primary_key = True)
    user = db.Column(db.Integer(), db.ForeignKey('Users.id'))
    role = db.Column(db.Integer(), db.ForeignKey('Roles.id'))
    time_created = db.Column(db.DateTime(), default=datetime.utcnow())

    @staticmethod
    def insert_user_roles(user_roles):
        if user_roles is None:
            user_roles = {"admin":"ADMIN",
                "doctor":"HIST_W",
                "researcher":"DATA_R",
                "researcher":"DATA_D"}
        for (k,v) in user_roles.items():
            user_role=UserRoles()
            user_role.user=Users.query.filter_by(username=k).first().id
            user_role.role=Roles.query.filter_by(permissions=v).first().id
            user_role.time_created = datetime.utcnow()
            db.session.add(user_role)
        db.session.commit()

# Пользователи
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100),index=True, unique=True)
    clinic = db.Column(db.Integer(), db.ForeignKey('Clinics.id'))
    time_create = db.Column(db.DateTime(), default=datetime.utcnow())
    password=db.Column(db.String(100))
    password_hash=db.Column(db.String(128))
    last_visit = db.Column(db.DateTime(), default=datetime.utcnow())
    confirmed=db.Column(db.Boolean(), default=False)
    roles = db.relationship('UserRoles', foreign_keys=[UserRoles.user],
                            backref=db.backref('users', lazy='joined'),
                            lazy='dynamic')

    def __repr__(self):
        return f'Пользователь {self.username}'

    #@property
    #def password(self):
    #    raise AttributeError('password is not a readable attribute')

    #@password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return(check_password_hash(self.password_hash, password))

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password':self.id, 'exp':time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id= jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Users.query.get(id)


    @staticmethod
    def insert_users():
        users = {"admin":{"username":"admin","email":"ikpservicemail@gmail.com","password":"admin","clinic":"1"},
                "doctor":{"username":"doctor","email":"ikp_doctor@gmail.com","password":"doctor","clinic":"1"},
            "researcher":{"username":"researcher","email":"ikp_researcher@gmail.com","password":"researcher","clinic":"1"}}
        for (k,v) in users.items():
            user=Users(username=v['username'],email=v['email'],password=v['password'])
            user.set_password(v["password"])
            user.time_create = datetime.utcnow()
            user.clinic = Clinics.query.get(v["clinic"]).id
            db.session.add(user)
        db.session.commit()

    def has_permissions(self, permission):
        if self.is_admin():
            return True
        user_role = UserRoles.query.filter_by(user=current_user.id, role=Roles.query.filter_by(permissions=permission).first().id).first()
        if user_role is None:
            return False
        return True

    def is_admin(self):
        current_user_is_admin = UserRoles.query.filter_by(user=current_user.id, role = Roles.query.filter_by(is_admin = True).first().id).first()
        if current_user_is_admin is None:
            return False
        return True

    def ping(self):
        self.last_visit = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

# Роли
class Roles(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=True)
    permissions = db.Column(db.String(10), index=True)
    is_admin = db.Column(db.Boolean(), index=True)
    users = db.relationship('UserRoles', foreign_keys=[UserRoles.role],
                            backref=db.backref('roles', lazy='joined'),
                            lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles={'Ведение справочников':{'permission':'REF_W', 'is_admin':False},
               'Просмотр справочников':{'permission':'REF_R', 'is_admin':False},
               'Ведение истории болезни':{'permission':'HIST_W', 'is_admin':False},
               'Чтение истории болезни':{'permission':'HIST_R', 'is_admin':False},
               'Отчеты просмотр':{'permission':'REP_R', 'is_admin':False},
               'Отчеты выгрузка':{'permission':'REP_D', 'is_admin':False},
               'Анализ данных просмотр':{'permission':'DATA_R', 'is_admin':False},
               'Анализ данных выгрузка':{'permission':'DATA_D', 'is_admin':False},
               'Администрирование':{'permission':'ADMIN', 'is_admin':True}}

        for (k,v) in roles.items():
            role = Roles.query.filter_by(description=k).first()
            if role is None:
                role = Roles(description=k, permissions=v['permission'],is_admin=v['is_admin'])
                db.session.add(role)
        db.session.commit()

# Клиники
class Clinics(db.Model):
    __tablename__ = 'Clinics'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100))
    users = db.relationship('Users',backref='clinic_of_users',lazy='dynamic')
    research_groups = db.relationship('ResearchGroups',backref='clinic_of_re_groups', lazy='dynamic')

    def __repr__(self):
        return f'Клиника {self.description}'


    @staticmethod
    def insert_clinics(dict_clinics):

        # Заполнение справочника групп из словаря
        # Сначала удаление значений справочника
        Clinics.query.delete()
        for i in dict_clinics:
            new_c = Clinics(id=i['id'],
                             description=i['description'])
            db.session.add(new_c)
        db.session.commit()


# Группы исследования

class ResearchGroups(db.Model):
    __tablename__ = 'ResearchGroups'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    clinic = db.Column(db.Integer(), db.ForeignKey('Clinics.id'))

    @staticmethod
    def insert_ResearchGroups(dict_rgroups):
    # Заполнение справочника групп из словаря
    # Сначала удаление значений справочника
        ResearchGroups.query.delete()
        for i in dict_rgroups:
            new_group = ResearchGroups(id=i['id'],
                                        description=i['description'],
                                        clinic=i['clinic'])
            db.session.add(new_group)
        db.session.commit()



# Причины исключения из исследования
class Reasons(db.Model):
    __tablename__ = 'Reasons'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=True)

# Диагнозы
class DiagnosesItems(db.Model):
    __tablename__ = 'DiagnosesItems'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=True)
    mkb10 = db.Column(db.String(20), unique=False)
    type = db.Column(db.String(30), unique=False, index = True)

# Врачи
class Doctors(db.Model):
    __tablename__ = 'Doctors'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(100), unique=False)
    second_name = db.Column(db.String(100), unique=False)
    fio = db.Column(db.String(100), unique=False)

# Протезы
class Prosthesis(db.Model):
    __tablename__ = 'Prosthesis'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    firm = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False)

# Осложнения
class Complications(db.Model):
    __tablename__ = 'Complications'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False, index = True)

# Виды операций
class OperationTypes(db.Model):
    __tablename__ = 'OperationTypes'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)

# Этапы операций
class OperationSteps(db.Model):
    __tablename__ = 'OperationSteps'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    order = db.Column(db.Integer(), unique=True)

# Наблюдения
class Events(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False, index = True)

# Список обследований
class Checkups(db.Model):
    __tablename__ = 'Checkups'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    is_mandatory = db.Column(db.Boolean(), unique=False, index = True)

# Группы Показателей
class IndicatorsGroups(db.Model):
    __tablename__ = 'IndicatorsGroups'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    indicators = db.relationship('Indicators', backref='groups', lazy='dynamic')

# Показатели
class Indicators(db.Model):
    __tablename__ = 'Indicators'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    group = db.Column(db.Integer(), db.ForeignKey('IndicatorsGroups.id'))
    unit = db.Column(db.String(20), unique=False)
    def_values = db.relationship('IndicatorsDefs', backref='def_indicators')
    norm_values = db.relationship('IndicatorsNorms', backref='norm_indicators')


# Допустимые значения показателей
class IndicatorsDefs(db.Model):
    __tablename__='IndicatorsDefs'
    id=db.Column(db.Integer(), primary_key=True)
    indicator = db.Column(db.Integer(), db.ForeignKey('Indicators.id'), index = True)
    text_value = db.Column(db.String(100), unique=False)
    num_value = db.Column(db.Numeric())

# Нормативные значения показателей
class IndicatorsNorms(db.Model):
    __tablename__='IndicatorsNorms'
    id=db.Column(db.Integer(), primary_key=True)
    indicator = db.Column(db.Integer(), db.ForeignKey('Indicators.id'), index = True)
    nvalue_from = db.Column(db.Numeric())
    nvalue_to = db.Column(db.Numeric())

# Пациенты
class Patients(db.Model):
    __tablename__ = 'Patients'
    id = db.Column(db.Integer(), primary_key=True)
    snils_hash =db.Column(db.String(128), unique=False)
#     clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinics.id'))
#     patient_snils = db.Column(db.String(11))
#     #fio = db.Column(db.String(100))
    birthdate = db.Column(db.Date())
    sex = db.Column(db.String(1), index=True)

    def __repr__(self):
        return f'Пациент {self.snils}'

    def get_snils_hash(self, snils):
        digest = md5(snils.lower().encode('utf-8')).hexdigest()
        self.snils_hash = digest

class LoadDictionary():

    def __init__(self, dict_list):
        self.dict_list = dict_list

    # Метод позволяет выбрать нужный справочник и загрузить его
    def switch_load(self,dict_name):
        default = "Метод загрузки отсутствует"
        return getattr(self, 'load_'+str(dict_name), lambda: default)()

    def load_Clinics(self):
        # Заполнение справочника групп из словаря
        # Сначала удаление значений справочника
        Clinics.query.delete()
        for i in self.dict_list:
            new_c = Clinics(id=i['id'],
                             description=i['description'])
            db.session.add(new_c)
        db.session.commit()

    def load_Reasons(self):
        # Заполнение справочника из словаря
        # Сначала удаление значений справочника
        Reasons.query.delete()
        for i in self.dict_list:
            new_c = Reasons(id=i['id'],
                             description=i['description'])
            db.session.add(new_c)
        db.session.commit()

    def load_DiagnosesItems(self):
        # Заполнение справочника из словаря
        # Сначала удаление значений справочника
        DiagnosesItems.query.delete()
        for i in self.dict_list:
            new_c = DiagnosesItems(id=i['id'],
                             description=i['description'],
                             mkb10=i['mkb10'],
                             type=i['type'])
            db.session.add(new_c)
        db.session.commit()

    def load_Roles(self):
        # Заполнение справочника из словаря
        # Сначала удаление значений справочника
        Roles.query.delete()
        for i in self.dict_list:
            new_c = Roles(id=i['id'],
                             description=i['description'],
                             permissions=i['permissions'],
                             is_admin=i['is_admin'])
            db.session.add(new_c)
        db.session.commit()


    def load_Prosthesis(self):
        # Заполнение справочника из словаря
        # Сначала удаление значений справочника
        Prosthesis.query.delete()
        for i in self.dict_list:
            new_c = Prosthesis(id=i['id'],
                             description=i['description'],
                             firm=i['firm'],
                             type=i['type'])
            db.session.add(new_c)
        db.session.commit()

    def load_Complications(self):
        # Заполнение справочника из словаря
        # Сначала удаление значений справочника
        Complications.query.delete()
        for i in self.dict_list:
            new_c = Complications(id=i['id'],
                             description=i['description'],
                             type=i['type'])
            db.session.add(new_c)
        db.session.commit()
