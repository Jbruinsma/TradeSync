from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length


class BrokerageForm(FlaskForm):
    brokerage = SelectField(
        'Oanda Account Type',
        choices=[('oanda', 'Oanda')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Next')