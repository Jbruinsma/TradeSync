from app.models.trade_account import TradeAccount


class ChildAccount(TradeAccount):
    def __init__(self, custom_name, brokerage, account_id, include_in_portfolio, master_account_id):
        super().__init__(custom_name, brokerage, account_id, include_in_portfolio)
        self.account_owner = None
        self.account_owner_email = None
        self.master_account_id = master_account_id

    def __str__(self):
        return f'{self.custom_name}, {self.account_id}'

    def set_settings(self, settings):
        self.brokerage.set_settings(settings)

    def get_master_account_name(self, user):
        master_account = user.master_accounts.get(self.master_account_id)
        if master_account:
            return master_account.custom_name
        return "Unknown Master Account"
    
    def get_risk_type(self):
        return self.brokerage.settings.risk_type
    
    def get_risk_setting(self):
        if self.get_risk_type() == 'multiplier':
            return f'{self.brokerage.settings.multiplier_factor}x'
        elif self.get_risk_type() == 'fixed':
            return f'{self.brokerage.settings.fixed_trade_size}x'
    def set_account_owner(self, account_owner= None, account_owner_email= None):
        if account_owner is not None:
            self.account_owner = account_owner
        if account_owner_email is not None:
            self.account_owner_email = account_owner_email

    def get_account_info(self):
        account_owner = "---" if self.account_owner is None else self.account_owner
        account_owner_email = "---" if self.account_owner_email is None else self.account_owner_email
        account_type = self.brokerage.get_account_type()
        return {'accountOwner': account_owner,
                'accountEmail': account_owner_email,
                'accountType': account_type
                }
    
    def get_api_key(self):
        return self.brokerage.get_api_key()
