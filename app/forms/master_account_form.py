from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import Length, DataRequired


class MasterAccountForm(FlaskForm):
    custom_name = StringField("Custom Account Name", validators=[DataRequired(), Length(min=3, max=50)])
    include_in_portfolio = SelectField('Include Account in Portfolio Value', choices=[('true', 'Yes'), ('false', 'No')], validators=[DataRequired()])
    submit = SubmitField("Add Master Account")