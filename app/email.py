from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with current_app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, **kwargs):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    Thread(target=send_async_email,
           args=(current_app, msg)).start()

def send_password_reset_email(user):
    token=user.get_reset_password_token()
    send_email( subject='[IKP] Reset Your password',
                sender = current_app.config['MAIL_ADMIN'],
                recipients=[user.email],
                text_body=render_template('auth/reset_password.txt',
                user=user, token=token),
                html_body=render_template('auth/reset_password.html',
                user=user, token=token))
