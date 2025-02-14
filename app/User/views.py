from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from datetime import datetime, time, timedelta
import pandas as pd

from app.models.User import Users, Metrics, Schedule, Colors
from app.extensions import db
from .forms import ScheduleForm


user = Blueprint('user', __name__, template_folder='templates')

# @user.route('/')
# def main_index():
#     user_list = db.session.execute(db.select(Users)).all()
#     for user in user_list:
#         user_metrics = db.session.execute(db.select(Metrics).filter(Metrics.operator_id == user[0].id)).all()
#         userWorkTime = timedelta(0)
#         for metrica in user_metrics:
#             userWorkTime = userWorkTime + timedelta(hours=metrica[0].StatusTimeInPlace.hour, minutes=metrica[0].StatusTimeInPlace.minute, seconds=metrica[0].StatusTimeInPlace.second)
#         print(f'ID пользователя: {user[0].id}. Время на рабочем месте = {userWorkTime}')
#         print('---')

#     return 'Blueprint Views.py Hello! User!'


@user.route('/')
def index():
    users = Users.query.all()
    colors = Colors.query.all()

    return render_template('User/index.html', users=users, colors=colors)
         
    
    
    colors = Colors.query.all()
    return render_template('User/index.html', users=users)


@user.route('/addexcel', methods=['GET', 'POST'])
def upload_file():
    return render_template('User/add_excel.html')


# @user.route('/addSchedule', methods=['GET', 'POST'])
# def upload_schedule():  
#     form = ScheduleForm()
    
#     return render_template('User/form_schedule.html', form=form)


@user.route('/data', methods=['GET', 'POST'])
def data_uploading():
    if request.method == 'POST':
        file = request.form['upload-file']
        data = pd.read_excel(file)
        print(data.head(6))
        print(data.tail(5))
        
        user_in_block = ['Vizor', 'Vizor2', 'Администратор', 'Оператор1', 'super123']

        for i in range(4, len(data)):
            metrica = data.iloc[i, 0:19].tolist()
            # print("---")
            # print(f"Metrica: {metrica}")
            
            if metrica[1] not in user_in_block and isinstance(metrica[1], str):
                SheetData = metrica[0]

                this_user = db.session.execute(db.select(Users.id, Users.name).filter(Users.name == metrica[1])).all()
                if not this_user:
                    print(metrica[1])
                    new_operator = Users(name=metrica[1])
                    db.session.add(new_operator)
                    db.session.commit()
                    print("Successfully added new operator")
                    this_user = db.session.execute(db.select(Users.id, Users.name).filter(Users.name == metrica[1])).all()
                operator_id = this_user[0].id   
                
                this_metrica = db.session.execute(db.select(Metrics).filter(Metrics.operator_id == operator_id).filter(Metrics.Data == SheetData)).all()
                
                if not this_metrica:
                    
                    StatusTimeInPlace = datetime.strptime(metrica[2], '%H:%M:%S').time()
                    StatusTimeBusy = datetime.strptime(metrica[3], '%H:%M:%S').time()
                    StatusTimeBreak = datetime.strptime(metrica[4], '%H:%M:%S').time()
                    StatusTimeGone = datetime.strptime(metrica[5], '%H:%M:%S').time()
                    StatusTimeNotAvailable = datetime.strptime(metrica[6], '%H:%M:%S').time()
                    
                    PercentInPlace = metrica[7]
                    
                    if isinstance(metrica[9], int): 
                        CountIncoming = metrica[9] 
                    else: 
                        CountIncoming = 0
                    
                    if isinstance(metrica[10], str): 
                        LenghtIncoming = datetime.strptime(metrica[10], '%H:%M:%S').time()
                    else: 
                        LenghtIncoming = time(00, 00, 00)
                        
                    if isinstance(metrica[11], str): 
                        IncomingAVG = datetime.strptime(metrica[11], '%H:%M:%S').time()
                    else: 
                        IncomingAVG = time(00, 00, 00)
                        
                    if isinstance(metrica[12], int): 
                        CountOutgoing = metrica[12] 
                    else: 
                        CountOutgoing = 0
                        
                    if isinstance(metrica[13], str): 
                        LenghtOutgoing = datetime.strptime(metrica[13], '%H:%M:%S').time()
                    else: 
                        LenghtOutgoing = time(00, 00, 00)
                    
                    if isinstance(metrica[14], str): 
                        OutgoingAVG = datetime.strptime(metrica[14], '%H:%M:%S').time()
                    else: 
                        OutgoingAVG = time(00, 00, 00)
                        
                    if isinstance(metrica[15], int): 
                        CountMissed = metrica[15] 
                    else: 
                        CountMissed = 0
                    
                    NewMetrica = Metrics(Data=SheetData, operator_id=operator_id, StatusTimeInPlace=StatusTimeInPlace, StatusTimeBusy=StatusTimeBusy, StatusTimeBreak=StatusTimeBreak,
                                        StatusTimeGone=StatusTimeGone, StatusTimeNotAvailable=StatusTimeNotAvailable, PercentInPlace=PercentInPlace, CountIncoming=CountIncoming,
                                        LenghtIncoming=LenghtIncoming, IncomingAVG=IncomingAVG, CountOutgoing=CountOutgoing, LenghtOutgoing=LenghtOutgoing, OutgoingAVG=OutgoingAVG,
                                        CountMissed=CountMissed)
                    # print(NewMetrica)
                    db.session.add(NewMetrica)
                    db.session.commit()
                    print('Экземпляр модели Metrics был успешно добавлен в базу данных')
                else:
                    print('Экземпляр модели Metrics уже существует')
            
        return render_template('User/data.html', data=data.to_dict())
    
    
@user.route('/load_schedules')
def load_schedules():
    schedules = Schedule.query.all()
    events = []
    for schedule in schedules:
        start_time = schedule.startTime.strftime('%H:%M')
        end_time = schedule.endTime.strftime('%H:%M')
        date = schedule.data.strftime('%Y-%m-%d')
        this_color = Colors.query.get_or_404(schedule.color_id)
        events.append({
            'title': f'{start_time} - {end_time}',
            'start': f'{date}T{start_time}',
            'end': f'{date}T{end_time}',
            'color': this_color.code,
            'color_id': this_color.id,
            'resourceId': schedule.operator_id,
            'id': schedule.id
        })
    return jsonify(events)

@user.route('/add_schedule', methods=['POST'])
def add_schedule():
    if request.method == 'POST':
        # Получаем данные из запроса
        user_id = request.form.get('user_id')
        color_id = request.form.get('color_id')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        # Проверяем наличие обязательных данных
        if not (user_id and color_id and date and start_time and end_time):
            return jsonify({'error': 'Не все данные были переданы'}), 400

        try:
            # Преобразуем время из строк в объекты time
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            # Создаем объект расписания и добавляем его в базу данных
            schedule = Schedule(
                operator_id=user_id,
                color_id=color_id,
                data=datetime.strptime(date, '%Y-%m-%d').date(),
                startTime=start_time_obj,
                endTime=end_time_obj
            )
            db.session.add(schedule)
            db.session.commit()

            return jsonify({'message': 'Расписание успешно добавлено'}), 200
        except Exception as e:
            print(f'Ошибка при добавлении расписания: {str(e)}')
            db.session.rollback()
            return jsonify({'error': 'Произошла ошибка при добавлении расписания'}), 500


@user.route('/delete_schedule/<event_id>', methods=['DELETE'])
def delete_schedule(event_id):
    this_schedule = Schedule.query.get_or_404(event_id)
    
    try:
        db.session.delete(this_schedule)
        db.session.commit()
        return jsonify({'message': 'ok'}), 200
    except:
	    return "При удалении статьи произошла ошибка"
    
    # return jsonify({'message': 'Schedule deleted successfully'}), 200


@user.route('/edit_schedule/<event_id>', methods=['GET', 'POST'])
def edit_schedule(event_id):
    this_schedule = Schedule.query.get_or_404(event_id)
    if request.method == 'POST':
        
        this_schedule.color_id = request.form['color_id']
        this_schedule.startTime = datetime.strptime(request.form['event_start'], '%H:%M').time()
        this_schedule.endTime = datetime.strptime(request.form["event_end"], '%H:%M').time()
        try:
            db.session.commit()
            return jsonify({'message': 'ok'}), 200
        except:
            return redirect(url_for('user.index'))
        
    else:
        # Fetch event details and render edit form
        # Example: event = db.get_event(event_id)
        # return render_template('edit_schedule.html', event=event)
        pass