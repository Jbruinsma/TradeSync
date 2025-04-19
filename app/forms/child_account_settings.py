from flask import session


from app import user_db
from app.utils.account_utils import get_master_accounts_list


from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField, RadioField
from wtforms.fields.numeric import IntegerField, DecimalField
from wtforms.fields.simple import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.fields import FieldList

class ChildAccountSettingsForm(FlaskForm):
    custom_name = StringField('Custom Name', validators=[DataRequired()])
    master_account = SelectField('Master Account', validators=[DataRequired()])
    include_in_portfolio = SelectField('Include Account in Portfolio Value', choices=[('true', 'Yes'), ('false', 'No')], validators=[DataRequired()])
    trade_types = FieldList(
        BooleanField(''),
        min_entries=3
    )
    order_types = FieldList(
        BooleanField(''),
        min_entries=4
    )  
    min_trade_size = DecimalField('Minimum Trade Size (Lots) | Optional', validators=[Optional(), NumberRange(min=0.01)])
    max_trade_size = DecimalField('Maximum Trade Size (Lots) | Optional', validators=[Optional(), NumberRange(min=0.01)])
    max_open_positions = IntegerField('Maximum Open Positions | Optional', validators=[Optional(), NumberRange(min=1)])
    risk_type = SelectField('Risk Type', choices=[('fixed', 'Fixed Lots'), ('multiplier', 'Multiplier')], validators=[DataRequired()])
    trade_closure = SelectField('Trade Closure Handling', choices=[('follow_master', 'Follow Master'), ('close_independently', 'Close Independently')], validators=[DataRequired()])
    submit = SubmitField('Next')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select_field_options = []
        try:
            username = session['username']
            user = user_db.search(username).val
            master_accounts = get_master_accounts_list(user)
            if master_accounts:
                for master_account in master_accounts:
                    select_field_options.append((master_account.account_id, master_account.custom_name))
        except KeyError:
            print("Error getting username")
        except Exception as e:
            print(f"Error getting master accounts: {e}")
        
        self.master_account.choices = select_field_options or [('', 'No master accounts available')]
        
        while len(self.trade_types) < 3:
            self.trade_types.append_entry()
        self.trade_types[0].label.text = 'All'
        self.trade_types[1].label.text = 'Buy'
        self.trade_types[2].label.text = 'Sell'
        
        while len(self.order_types) < 4:
            self.order_types.append_entry()
        self.order_types[0].label.text = 'All'
        self.order_types[1].label.text = 'Market'
        self.order_types[2].label.text = 'Limit'
        self.order_types[3].label.text = 'Stop'

    def get_trade_types_dict(self):
        return {
            'all': self.trade_types[0].data,
            'buy': self.trade_types[1].data,
            'sell': self.trade_types[2].data
        }

    def get_order_types_dict(self):
        return {
            'all': self.order_types[0].data,
            'market': self.order_types[1].data,
            'limit': self.order_types[2].data,
            'stop': self.order_types[3].data
        }
