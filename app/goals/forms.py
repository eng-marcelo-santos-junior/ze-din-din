from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class GoalForm(FlaskForm):
    name = StringField(
        'Nome da meta',
        validators=[DataRequired('Informe o nome da meta.'), Length(max=100)],
        render_kw={'placeholder': 'Ex: Reserva de emergência, Viagem...'},
    )
    target_amount = StringField(
        'Valor alvo',
        validators=[DataRequired('Informe o valor alvo.')],
        render_kw={'placeholder': '0,00'},
    )
    target_date = DateField('Data alvo', validators=[Optional()])
    account_id = SelectField(
        'Conta vinculada',
        coerce=int,
        validators=[Optional()],
    )
    submit = SubmitField('Salvar meta')


class ContributeForm(FlaskForm):
    amount = StringField(
        'Valor do aporte',
        validators=[DataRequired('Informe o valor do aporte.')],
        render_kw={'placeholder': '0,00'},
    )
    submit = SubmitField('Registrar aporte')
