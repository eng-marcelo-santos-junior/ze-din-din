from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


CURRENCY_CHOICES = [
    ('BRL', 'Real Brasileiro (R$)'),
    ('USD', 'Dólar Americano ($)'),
    ('EUR', 'Euro (€)'),
]


class FamilyForm(FlaskForm):
    name = StringField(
        'Nome da família',
        validators=[DataRequired(message='Informe o nome da família.'), Length(min=2, max=100)],
        render_kw={'placeholder': 'Ex: Família Silva'},
    )
    currency = SelectField(
        'Moeda principal',
        choices=CURRENCY_CHOICES,
        default='BRL',
    )
    submit = SubmitField('Criar família')
