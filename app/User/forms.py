from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired
from app.models.User import Users


class ScheduleForm(FlaskForm):
    operator = SelectField("Оператор: ", coerce=int, choices=[], validators=[DataRequired()])
    name = StringField("ФИО: ")
    isActive = BooleanField("Активен", default=True)
    submit = SubmitField("Записать")
    
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.operator.choices = [(user.id, user.name) for user in Users.query.all()]