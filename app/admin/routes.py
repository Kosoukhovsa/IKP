from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.admin import bp
from app.admin.forms import UserRole, UserRoleFilter
from app.models import Users, Clinics, UserRoles, Roles
from datetime import datetime

@bp.route('/user_role_edit', methods = ['GET','POST'])
def user_role():
    UserForm = UserRole()
    UserFilterForm = UserRoleFilter()
    page = request.args.get('page',1,type=int)

    user_filter_id = session.get('user_filter_id')
    if user_filter_id is not None:
        pagination =  UserRoles.query.filter_by(user=user_filter_id).paginate(page,5,error_out=False)
    else:
        pagination =  UserRoles.query.paginate(page,5,error_out=False)
    userroles = pagination.items

    if UserForm.submit_ok.data and UserForm.validate_on_submit():
        user = Users.query.get(UserForm.user.data)
        role = Roles.query.get(UserForm.role.data)
        user_role = UserRoles.query.filter_by(user=user.id, role=role.id).first()
        if user_role is not None and UserForm.action.data == 1:
            flash('Данному пользователю роль уже назначена', category='warning')
        elif user_role is None and UserForm.action.data == 1:
            user_role = UserRoles(user=user.id, role=role.id)
            db.session.add(user_role)
            db.session.commit()
            flash('Полномочия назначены', category='info')
        elif user_role is None and UserForm.action.data == 2:
            flash('Таких полномочий нет', category='warning')
        elif user_role is not None and UserForm.action.data == 2:
            db.session.delete(user_role)
            db.session.commit()
            flash('Полномочия удалены', category='warning')
    if UserFilterForm.submit_filter.data and UserFilterForm.validate_on_submit():
        user_filter = Users.query.get(UserFilterForm.user_filter.data)
        pagination =  UserRoles.query.filter_by(user=user_filter.id).paginate(page,5,error_out=False)
        userroles = pagination.items
        session['user_filter_id']=user_filter.id

    return render_template('admin/user_role.html', Panel='UserRoles', UserForm=UserForm, UserFilterForm=UserFilterForm, userroles=userroles,
                            title='Назначение полномочий', Users=Users, Roles=Roles,
                            pagination=pagination)
