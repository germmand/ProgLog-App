from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired

class ResponseForm(FlaskForm): 
    answered_node = RadioField('Respuesta', [
                               InputRequired(message='Debe seleccionar una respuesta.')],
                               coerce=int)
    subject_name  = StringField('Tema', [
                                InputRequired()])
    current_node  = StringField('Pregunta', [
                                InputRequired()])
