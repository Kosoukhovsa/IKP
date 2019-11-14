from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Users


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Эдектронная почта', validators=[DataRequired(), Email()])
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = Users.query.filter_by(description = username.data).first()
        if user is not None:
            raise ValidationError('Пользователь уже существует')

    def validate_email(self, email):
        user = Users.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError(f'Пользователь с таким email {email.data} уже существует')
