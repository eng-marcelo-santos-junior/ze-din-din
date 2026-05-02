from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

BILL_TYPE_CHOICES = [
    ('PAYABLE', 'A Pagar'),
    ('RECEIVABLE', 'A Receber'),
]


class BillForm(FlaskForm):
    description = StringField(
        'Descrição',
        validators=[DataRequired('Informe a descrição.'), Length(max=200)],
        render_kw={'placeholder': 'Ex: Aluguel, Fatura do cartão...'},
    )
    type = SelectField('Tipo', choices=BILL_TYPE_CHOICES, default='PAYABLE')
    amount = StringField(
        'Valor',
        validators=[DataRequired('Informe o valor.')],
        render_kw={'placeholder': '0,00'},
    )
    due_date = DateField('Data de vencimento', validators=[DataRequired()])
    account_id = SelectField(
        'Conta (para pagamento)',
        coerce=int,
        validators=[Optional()],
    )
    category_id = SelectField(
        'Categoria',
        coerce=int,
        validators=[Optional()],
    )
    submit = SubmitField('Salvar')


class PayBillForm(FlaskForm):
    account_id = SelectField('Conta', coerce=int, validators=[DataRequired()])
    paid_date = DateField('Data do pagamento', validators=[DataRequired()])
    submit = SubmitField('Confirmar pagamento')
