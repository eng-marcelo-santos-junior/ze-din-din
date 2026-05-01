from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

MONTH_CHOICES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]


class BudgetForm(FlaskForm):
    category_id = SelectField(
        'Categoria de despesa',
        coerce=int,
        validators=[DataRequired('Selecione uma categoria.')],
    )
    month = SelectField(
        'Mês',
        coerce=int,
        choices=MONTH_CHOICES,
        validators=[DataRequired()],
    )
    year = IntegerField(
        'Ano',
        validators=[DataRequired(), NumberRange(min=2000, max=2100)],
    )
    planned_amount = StringField(
        'Valor planejado',
        validators=[DataRequired('Informe o valor planejado.')],
        render_kw={'placeholder': '0,00'},
    )
    submit = SubmitField('Salvar orçamento')
