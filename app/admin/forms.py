from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from app.models import Users, Clinics, Roles, UserRoles


class UserRole(FlaskForm):
    user = SelectField('Имя пользователя', coerce = int, validators=[DataRequired()])
    role = SelectField('Роль', coerce = int, validators=[DataRequired()])
    action = RadioField('Действие', choices=[(1,'Добавить'),(2,'Удалить')], default=1, coerce=int)
    submit_ok = SubmitField('Ok')

    def __init__(self, *args, **kwargs):
        super(UserRole, self).__init__(*args, **kwargs)
        self.user.choices=[(user.id, user.username)
                              for user in Users.query.order_by(Users.id).all()]
        self.role.choices=[(role.id, role.description)
                              for role in Roles.query.order_by(Roles.id).all()]


class UserRoleFilter(FlaskForm):
    user_filter = SelectField('Пользователи', coerce = int)
    role_filter = SelectField('Роли', coerce = int)
    submit_filter = SubmitField('Фильтр')

    def __init__(self, *args, **kwargs):
        super(UserRoleFilter, self).__init__(*args, **kwargs)
        self.user_filter.choices=[(user.id, user.username)
                              for user in Users.query.order_by(Users.id).all()]
        #self.user_filter.choices.insert(0,(0,'All'))
        self.role_filter.choices=[(role.id, role.description)
                              for role in Roles.query.order_by(Roles.id).all()]
        #self.role_filter.choices.insert(0,(0,'All'))
