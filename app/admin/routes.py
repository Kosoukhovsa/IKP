from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.admin import bp
from app.admin.forms import UserRole
from app.models import Users, Clinics, UserRoles, Roles
from datetime import datetime

@bp.route('/user_role', methods = ['GET','POST'])
def user_role():
    form = UserRole()
    if form.validate_on_submit():
        user = Users.query.get(form.user.data)
        role = Roles.query.get(form.role.data)
        user_role = UserRoles.query.filter_by(user=user.id, role=role.id).first()
        if user_role is not None and form.action.data == 1:
            flash('Данному пользователю роль уже назначена', category='warning')
        elif user_role is None and form.action.data == 1:
            user_role = UserRoles(user=user.id, role=role.id)
            db.session.add(user_role)
            db.session.commit()
            flash('Полномочия назначены', category='info')
        elif user_role is None and form.action.data == 2:
            flash('Таких полномочий нет', category='warning')
        elif user_role is not None and form.action.data == 2:
            db.session.delete(user_role)
            db.session.commit()
            flash('Полномочия удалены', category='warning')
    page = request.args.get('page',1,type=int)
    pagination =  UserRoles.query.paginate(page,5,error_out=False)
    #userroles=UserRoles.query.all()
    userroles = pagination.items
    return render_template('admin/user_role.html', form=form, userroles=userroles,
                            title='Назначение полномочий', Users=Users, Roles=Roles,
                            pagination=pagination)
