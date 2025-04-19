from flask_wtf import FlaskForm
from wtforms.fields.numeric import DecimalField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class FixedLotSettings(FlaskForm):
    fixed_lot_trade_size = DecimalField("Fixed Trade Size (Pips) | Optional", validators=[Optional(), NumberRange(min=0.01, max=float(40))])
    fixed_stop_loss = DecimalField("Fixed Stop Loss (Pips) | Optional", validators=[Optional(), NumberRange(min=0.01, max=float("inf"))])
    fixed_take_profit = DecimalField("Fixed Take Profit (Pips) | Optional", validators=[Optional(), NumberRange(min=0.01, max=float("inf"))])
    submit = SubmitField("Complete")