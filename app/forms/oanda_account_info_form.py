from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired


from app.services.account_info_validation import validate_oanda_credentials


class NewOandaTradingAccount(FlaskForm):
    api_key = StringField('Oanda API Key', validators=[DataRequired()])
    account_id = StringField('Oanda Account ID', validators=[DataRequired()])
    account_type = SelectField(
        'Oanda Account Type',
        choices=[('demo', 'Demo'), ('live', 'Live')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Next')

    def validate(self, extra_validators=None):
        """Override the default validate method to add custom validation"""
        if not super().validate(extra_validators=extra_validators):
            return False
        
        is_live = self.account_type.data == 'live'
        
        if not validate_oanda_credentials(self.api_key.data, self.account_id.data, is_live):
            self.api_key.errors.append('Invalid Oanda credentials')
            return False
            
        return True
