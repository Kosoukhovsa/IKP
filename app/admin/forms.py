from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from app.models import Users, Clinics, Roles, UserRoles


class UserRole(FlaskForm):
    user = SelectField('Имя пользователя', coerce = int)
    role = SelectField('Роль', coerce = int)
    action = RadioField('Действие', choices=[(1,'Добавить'),(2,'Удалить')], default=1, coerce=int)
    submit = SubmitField('Ok')

    def __init__(self, *args, **kwargs):
        super(UserRole, self).__init__(*args, **kwargs)
        self.user.choices=[(user.id, user.username)
                              for user in Users.query.order_by(Users.id).all()]
        self.role.choices=[(role.id, role.description)
                              for role in Roles.query.order_by(Roles.id).all()]
