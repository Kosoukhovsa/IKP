from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.history import bp
from app.history.forms import HistoryFilterForm, HistoryMainForm, IndicatorsForm, \
                              IndicatorItemForm, HistoryMainDiagnosForm, HistoryOtherDiagnosForm,\
                              AmbulanceMainForm
from app.models import Histories, Clinics, Diagnoses, Patients, Indicators, HistoryEvents,\
                       IndicatorValues
from datetime import datetime
from hashlib import md5
from app.history.history_tools import CreateHistory, UpdateHistory, FillHistoryForm, \
                                    AddMainDiagnos, AddOtherDiagnos, CreateAmbulance, \
                                    FillAmbulanceForm, UpdateAmbulance



# Список историй болезни
@bp.route('/history_select', methods = ['GET','POST'])
def history_select():

    FilterForm = HistoryFilterForm()
    page = request.args.get('page',1,type=int)

    clinic_filter_id = session.get('clinic_filter_id')
    snils_filter_hash = session.get('snils_filter_hash')
    history_list = Histories.query
    if clinic_filter_id is not None:
        history_list = history_list.filter(Histories.clinic==clinic_filter_id)

    if snils_filter_hash is not None:
        patient = Patients.query.filter(Patients.snils_hash==snils_filter_hash).first()
        history_list = history_list.filter(Histories.patient==patient)


    pagination =  history_list.paginate(page,5,error_out=False)
    histories = pagination.items

    if FilterForm.submit_filter.data and FilterForm.validate_on_submit():
# Фильтрация списка
        history_list = Histories.query
        if FilterForm.clinic_filter.data != 0:
# Выбрано значение ( не All)
            history_list = history_list.filter(Histories.clinic==FilterForm.clinic_filter.data)
            session['clinic_filter_id']= FilterForm.clinic_filter.data
# Выбрано значение ALL - снять фильтр
        if FilterForm.clinic_filter.data == 0:
            session['clinic_filter_id'] = None

        if FilterForm.snils_filter.data != '':
# Выбрано значение ( не All)
            digest = md5(FilterForm.snils_filter.data.lower().encode('utf-8')).hexdigest()
            patient = Patients.query.filter(Patients.snils_hash==digest).first()
            if patient != None:
                history_list = history_list.filter(Histories.patient==patient.id)
                session['snils_filter_hash']= digest
            else:
                flash('Пациента с указанным СНИЛС не существует', category='warning')


# Выбрано значение ALL - снять фильтр
        if FilterForm.snils_filter.data == '':
            session['snils_filter_hash'] = None

        pagination =  history_list.paginate(page,5,error_out=False)
        histories = pagination.items


    return render_template('history/history_select.html', HistoryFilterForm=FilterForm,
                            title='Поиск истории болезни', histories=histories, pagination=pagination)


# Редактирование истории болезни
@bp.route('/history_edit/<h>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# pill - номер закладки в форме
def history_edit(h, pill):
    MainForm = HistoryMainForm()
    FirstForm = IndicatorsForm()
    MainDiagnosForm = HistoryMainDiagnosForm()
    OtherDiagnosForm = HistoryOtherDiagnosForm()
    if h != '0':
        history = Histories.query.get(h)

        # сохранение истории болезни
    if MainForm.submit.data and MainForm.validate_on_submit():
        pill = 1
        if h == '0':
            # Это ввод новой истории
            history = CreateHistory(MainForm)
        else:
            # Обновление истории
            history = UpdateHistory(MainForm, h)

        if  history != None:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.history_edit', h=history.id, pill=pill))
    if MainDiagnosForm.submit.data and MainDiagnosForm.validate_on_submit():
        pill = 3
        main_diagnose = AddMainDiagnos(MainDiagnosForm, h)
        if main_diagnose is not None:
            flash('Данные сохранены', category='info')

        return redirect(url_for('history.history_edit', h=history.id, pill=pill))

    if OtherDiagnosForm.submit.data and OtherDiagnosForm.validate_on_submit():
        pill = 3
        other_diagnose = AddOtherDiagnos(OtherDiagnosForm, h)
        if other_diagnose is not None:
            flash('Данные сохранены', category='info')

        return redirect(url_for('history.history_edit', h=history.id, pill=pill))

    if h != '0':
        # Заполнение формы данными из базы
        form_list = FillHistoryForm(MainForm, FirstForm, MainDiagnosForm, h)
        MainForm = form_list[0]
        FirstForm = form_list[1]
        MainDiagnosForm = form_list[2]
        event_id = form_list[3].id
        items = form_list[4]
        diagnoses_items = form_list[5]
    else:
        items = []
        event_id = 0
    return render_template('history/history_edit.html', HistoryMainForm=MainForm,
                            h=h, items = items, FirstForm=FirstForm,
                            MainDiagnosForm = MainDiagnosForm,
                            OtherDiagnosForm = OtherDiagnosForm,
                            event = event_id,
                            diagnoses_items = diagnoses_items,
                            pill=pill)


# Сохранение показателей первичного обращения
@bp.route('/save_indicators/<h>/<e>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# e - HistoryEvents.id
# pill - номер закладки в форме
def save_indicators(h, e, pill):
    if 'save_indicators' in request.form: #and FirstForm.validate_on_submit():
        event = HistoryEvents.query.get(e)
        if request.form.get('date_begin'):
            event.date_begin = datetime.strptime(request.form.get('date_begin'), '%Y-%m-%d').date()
        db.session.add(event)
        num_values = request.form.getlist('num_value')
        comments = request.form.getlist('comment')
        ids = request.form.getlist('indicator_id')
        # Получим список всех показателей физ параметров истории болезни
        indicator = IndicatorValues.query.get(ids[0])
        indicator.num_value = num_values[0]
        indicator.comment = comments[0]
        db.session.add(indicator)
        indicator = IndicatorValues.query.get(ids[1])
        indicator.num_value = num_values[1]
        indicator.comment = comments[1]
        db.session.add(indicator)
        indicator = IndicatorValues.query.get(ids[2])
        if int(num_values[0]) != 0:
            indicator.num_value = int(num_values[1])/(int(num_values[0])/100)**2
        indicator.comment = comments[2]
        db.session.add(indicator)
        db.session.commit()
        flash('Данные сохранены', category='info')

    history_event = HistoryEvents.query.get(e)
    if history_event.event == 1:
        # Первичный прием
        return redirect(url_for('history.history_edit', h=h, pill=pill))
    elif history_event.event == 2:
        # Амбулаторный  прием
        return redirect(url_for('history.ambulance_edit', h=h, e=e, pill=pill))

# История болезни / Диагнозы
@bp.route('/diagnose_delete/<h>/<d>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# d - Diagnoses.id
# pill - номер закладки в форме
def diagnose_delete(h,d,pill):
    diagnose = Diagnoses.query.get(d)
    db.session.delete(diagnose)
    db.session.commit()

    return redirect(url_for('history.history_edit', h=h, pill=pill))


# Редактирование амбулаторного приема
@bp.route('/ambulance_edit/<h>/<e>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# e - HistoryEvents.id
# pill - номер закладки в форме
def ambulance_edit(h, e, pill):
    history = Histories.query.get(h)
    AmbulanceForm = AmbulanceMainForm()
    if AmbulanceForm.submit.data and AmbulanceForm.validate_on_submit():
        pill = 1
        if e == '0':
            # Это ввод нового амбулаторного приема
            event = CreateAmbulance(AmbulanceForm, h)
        else:
            # Обновление амбулаторного приема
            print(AmbulanceForm.doctor.data)
            event = UpdateAmbulance(AmbulanceForm, h, e)

        if  event != None:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.ambulance_edit', h=h, e=event.id, pill=pill))

    if e != '0':
        # Открываем уже сущестующее посещение
        event = HistoryEvents.query.get(e)
        # Заполнение формы данными из базы
        form_list = FillAmbulanceForm(AmbulanceForm, history, event)
        AmbulanceForm = form_list[0]
        items = form_list[1]
        print(items)
    else:
        items = []

    return render_template('history/ambulance.html', AmbulanceMainForm = AmbulanceForm,
                            h=h, e=e,  history=history, items = items, pill=pill)
