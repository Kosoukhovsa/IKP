from flask import render_template, redirect, url_for, flash, request, session
from app import db
from app.history import bp
from app.history.forms import HistoryFilterForm, HistoryMainForm, IndicatorsForm, IndicatorItemForm
from app.models import Histories, Clinics, Diagnoses, Patients, Indicators, HistoryEvents,\
                       IndicatorValues, DiagnosesItems
from datetime import datetime
from hashlib import md5

# Создание новой истории болезни
def CreateHistory(MainForm):
    digest = md5(MainForm.snils.data.lower().encode('utf-8')).hexdigest()
    if Patients.get_patient_by_snils(digest) is None:
        # Новый пациент
        new_patient = Patients()
        new_patient.birthdate = MainForm.birthdate.data
        new_patient.sex = MainForm.sex.data
        new_patient.snils_hash = digest
        db.session.add(new_patient)
        db.session.commit()
        # Новая история болезни
        new_hist = Histories()
        new_hist.clinic = MainForm.clinic.data
        new_hist.hist_number = MainForm.hist_number.data
        new_hist.date_in = MainForm.date_in.data
        new_hist.patient = new_patient.id
        new_hist.research_group = MainForm.research_group.data
        new_hist.doctor_researcher = MainForm.doctor_researcher.data
        new_hist.date_research_in = MainForm.date_research_in.data
        new_hist.date_research_out = MainForm.date_research_out.data
        new_hist.reason = MainForm.reason.data
        db.session.add(new_hist)
        db.session.commit()
        # Пустое первичное обращение
        new_event = HistoryEvents()
        new_event.clinic = MainForm.clinic.data
        new_event.history = new_hist.id
        new_event.patient = new_patient.id
        new_event.date_begin = new_hist.date_in
        new_event.event = 1
        db.session.add(new_event)
        db.session.commit()
        # Показатели: Физические параметры (самооценка при первичном опросе)
        indicators = Indicators.query.filter(Indicators.group==11).all()
        for i in indicators:
            new_i = IndicatorValues()
            new_i.clinic = MainForm.clinic.data
            new_i.history = new_hist.id
            new_i.patient = new_patient.id
            new_i.history_event = new_event.id
            new_i.indicator = i.id
            db.session.add(new_i)
            db.session.commit()
        return(new_hist)

    else:
        flash('Пациент с указанным СНИЛС уже есть в базе', category='warning')
        return(None)

# Обновление истории болезни
def UpdateHistory(MainForm, h):
        history = Histories.query.get(h)
        if history is None:
            return(None)
        else:
            patient =  Patients.query.get(history.patient)
            if patient is not None:
                patient.birthdate = MainForm.birthdate.data
                patient.sex = MainForm.sex.data
                db.session.add(patient)
                db.session.commit()
            # Новая история болезни
            history.clinic = MainForm.clinic.data
            history.hist_number = MainForm.hist_number.data
            history.date_in = MainForm.date_in.data
            history.patient = patient.id
            history.research_group = MainForm.research_group.data
            history.doctor_researcher = MainForm.doctor_researcher.data
            history.date_research_in = MainForm.date_research_in.data
            history.date_research_out = MainForm.date_research_out.data
            history.reason = MainForm.reason.data
            db.session.add(history)
            db.session.commit()
            return(history)

# Заполнение формы истории болезни
def FillHistoryForm(MainForm, FirstForm, MainDiagnosForm, h):
    #MainForm = HistoryMainForm()
    history = Histories.query.get(h)
    if history != None:
        patient = Patients.query.get(history.patient)
        MainForm.clinic.data = history.clinic
        MainForm.hist_number.data = history.hist_number
        MainForm.snils.data = patient.snils_hash
        MainForm.birthdate.data = patient.birthdate
        MainForm.sex.data = patient.sex
        MainForm.date_in.data = history.date_in
        MainForm.research_group.data = history.research_group
        MainForm.doctor_researcher.data = history.doctor_researcher
        MainForm.date_research_in.data = history.date_research_in
        MainForm.date_research_out.data = history.date_research_out
        MainForm.reason.data = history.reason
        # Список показателей первичного обращения
        event = HistoryEvents.query.filter(HistoryEvents.history==h, HistoryEvents.event==1 ).first()
        FirstForm.date_begin.data = event.date_begin
        indicators = IndicatorValues.query.filter(IndicatorValues.history==h, IndicatorValues.history_event==event.id).all()
        items = []
        for i in indicators:
            item = {}
            indicator = Indicators.query.get(i.indicator)
            item['id'] = i.id
            item['indicator'] = i.indicator
            item['description'] = indicator.description
            if i.num_value == None:
                item['num_value'] = 0
            else:
                item['num_value'] = int(i.num_value)
            if i.comment == None:
                item['comment'] = ''
            else:
                item['comment'] = i.comment
            items.append(item)
        # список сопутствующих диагнозов для отображения в форме
        diagnoses = Diagnoses.query.filter(Diagnoses.history==h).all()
        diagnoses_items = []
        main_diagnos = None
        for d in diagnoses:
            diagnose_item = DiagnosesItems.query.get(d.diagnose)
            if diagnose_item.type == 'Основной':
                main_diagnos = d
            else:
                item = {}
                item['id'] = d.id
                item['description'] = diagnose_item.description
                item['mkb10'] = diagnose_item.mkb10
                item['date_created'] = d.date_created
                diagnoses_items.append(item)

        if main_diagnos is not None:
            MainDiagnosForm.diagnos.data = main_diagnos.diagnose
            MainDiagnosForm.side_damage.data = main_diagnos.side_damage
            MainDiagnosForm.date_created.data = main_diagnos.date_created

        return([MainForm, FirstForm, MainDiagnosForm, event, items, diagnoses_items])

    else:
        # История не найдена
        return(None)

# Добавление основного диагноза
def AddMainDiagnos(MainDiagnosForm, h):
    history = Histories.query.get(h)
    main_diagnose = None
    if history is not None:
        # Создать или обновить основной диагноз
        # Основной диагноз может быть только один
        main_diagnose = Diagnoses.query.filter(Diagnoses.history==h,Diagnoses.diagnose==MainDiagnosForm.diagnos.data).first()
        if main_diagnose is not None:
            # Такой диагноз уже есть
            # Обновить атрибуты
            main_diagnose.side_damage = MainDiagnosForm.side_damage.data
            main_diagnose.date_created = MainDiagnosForm.date_created.data
        else:
            # Такой основной диагноз еще отсутствует
            diagnoses = Diagnoses.query.filter(Diagnoses.history==h).all()
            for d  in diagnoses:
                diagnose_item = DiagnosesItems.query.get(d.diagnose)
                if diagnose_item.type == 'Основной':
                    # Уже есть основной диагноз но другой: будет перезаписан
                    main_diagnose = d
                    main_diagnose.diagnose = MainDiagnosForm.diagnos.data
                    main_diagnose.side_damage = MainDiagnosForm.side_damage.data
                    main_diagnose.date_created = MainDiagnosForm.date_created.data

            if main_diagnose is None:
                # Создаем основной диагноз
                main_diagnose = Diagnoses()
                main_diagnose.history = h
                main_diagnose.clinic = history.clinic
                main_diagnose.patient = history.patient
                main_diagnose.diagnose = MainDiagnosForm.diagnos.data
                main_diagnose.side_damage = MainDiagnosForm.side_damage.data
                main_diagnose.date_created = MainDiagnosForm.date_created.data

        db.session.add(main_diagnose)
        db.session.commit()

    return(main_diagnose)


# Добавление основного диагноза
def AddOtherDiagnos(OtherDiagnosForm, h):
    other_diagnose = None
    # Если диагноз уже добавлен - предупреждение
    other_diagnose = Diagnoses.query.filter(Diagnoses.history==h,Diagnoses.diagnose==OtherDiagnosForm.diagnos.data).first()
    if other_diagnose is not None:
        flash('Такой диагноз уже есть', category='warning')
        return(None)

    # Создаем новый диагноз
    history = Histories.query.get(h)
    other_diagnose = Diagnoses()
    other_diagnose.history = h
    other_diagnose.clinic = history.clinic
    other_diagnose.patient = history.patient
    other_diagnose.diagnose = OtherDiagnosForm.diagnos.data
    #other_diagnose.side_damage = MainDiagnosForm.side_damage.data
    other_diagnose.date_created = OtherDiagnosForm.date_created.data
    db.session.add(other_diagnose)
    db.session.commit()
    return(other_diagnose)

# Создание нового амбулаторного приема
def CreateAmbulance(AmbulanceForm, h):
    history = Histories.query.get(h)
    ambulance = HistoryEvents.query.filter(HistoryEvents.history==h,HistoryEvents.event==2).first()
    if ambulance is None:
        # Создаем амбулаторный прием
        ambulance = HistoryEvents()
        ambulance.clinic = history.clinic
        ambulance.history = history.id
        ambulance.patient = history.patient
        ambulance.event = 2
        ambulance.date_begin = AmbulanceForm.date_begin.data
        ambulance.doctor = AmbulanceForm.doctor.data
        db.session.add(ambulance)
        # Показатели: Физические параметры (самооценка при первичном опросе)
        indicators = Indicators.query.filter(Indicators.group==11).all()
        for i in indicators:
            new_i = IndicatorValues()
            new_i.clinic = ambulance.clinic
            new_i.history = ambulance.history
            new_i.patient = ambulance.patient
            new_i.history_event = ambulance.id
            new_i.indicator = i.id
            db.session.add(new_i)
        db.session.commit()
    return(ambulance)

# Создание нового амбулаторного приема
def UpdateAmbulance(AmbulanceForm, h, e):
    history = Histories.query.get(h)
    ambulance = HistoryEvents.query.get(e)
    if ambulance is not None:
        ambulance.doctor = AmbulanceForm.doctor.data
        ambulance.date_begin = AmbulanceForm.date_begin.data
        db.session.add(ambulance)
        db.session.commit()

    return(ambulance)


# Заполнение формы амбулаторного посещения
def FillAmbulanceForm(AmbulanceForm, history, event):
    #MainForm = HistoryMainForm()
    if event != None:
        AmbulanceForm.doctor.data = event.doctor
        AmbulanceForm.date_begin.data = event.date_begin
        indicators = IndicatorValues.query.filter(IndicatorValues.history==history.id, IndicatorValues.history_event==event.id).all()
        items_11 = [] # Физические параметры
        for i in indicators:
            indicator = Indicators.query.get(i.indicator)
            print(indicator.group)
            if indicator.group == 11:
                # Это физические параметры
                item = {}
                item['id'] = i.id
                item['indicator'] = i.indicator
                item['description'] = indicator.description
                if i.num_value == None:
                    item['num_value'] = 0
                else:
                    item['num_value'] = int(i.num_value)
                if i.comment == None:
                    item['comment'] = ''
                else:
                    item['comment'] = i.comment
                items_11.append(item)

        return([AmbulanceForm, items_11])

    else:
        # История не найдена
        return(None)
