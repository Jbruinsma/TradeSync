from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class MultiplierSettings(FlaskForm):
    multiplier_factor = DecimalField("Multiplier Factor (%)", validators=[DataRequired(), NumberRange(min=0.01, max=float("inf"))])
    submit = SubmitField("Complete")
