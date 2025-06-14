from app.utils.password_utils import hash_password, verify_password
from datetime import datetime


from app.models.brokerage.oanda_brokerage.oanda import OANDA
from app.models.master_account import MasterAccount


class User:

    def __init__(self, username, password):
        self.username = username
        self.password_hash = hash_password(password)
        self.join_date = datetime.now()
        self.master_accounts = {}
        self.copier_logs = []


    def __str__(self):
        formatted_date = self.join_date.strftime("%B %d, %Y")
        return f"User(username={self.username}, joined={formatted_date})"

    def get_formatted_join_date(self):
        """Returns join date in a readable format like 'March 30, 2025'"""
        return self.join_date.strftime("%B %d, %Y")

    def verify_password(self, password):
        return verify_password(password, self.password_hash)
    
    def register_master_account(self, new_account_info, settings):
        account_id = new_account_info['account_id']
        custom_name = settings.custom_name.data
        api_key = new_account_info['api_key']
        trade_account_type = True if new_account_info['account_type'] == 'live' else False
        include_in_portfolio_value = True if settings.include_in_portfolio.data == "true" else False
        brokerage = new_account_info['brokerage']

        if account_id in self.master_accounts:
            print(f'Account {account_id} already exists')
            return
        
        for master_account in self.master_accounts.values():
            if master_account.has_child_account_id(account_id):
                print(f'Account {account_id} already exists as a child account')
                return
        
        if brokerage == 'oanda':
            brokerage = OANDA(account_id=account_id, api_key=api_key, is_live=trade_account_type)

        new_master_account = MasterAccount(
             custom_name=custom_name, 
             brokerage= brokerage, 
             account_id=account_id, 
             api_key=api_key, 
             is_live=trade_account_type, 
             include_in_portfolio=include_in_portfolio_value
             )
        
        self.master_accounts[account_id] = new_master_account

    def register_child_account(self, new_account_info, account_settings, risk_settings):
        master_account_id = account_settings['master_account']
        account_id = new_account_info['account_id']

        if master_account_id not in self.master_accounts:
            print(f'Master account {master_account_id} not found')
            return False

        master_account = self.master_accounts[master_account_id]
        
        if account_id in self.master_accounts:
            print(f'Account {account_id} already exists as a master account')
            return False

        for existing_master in self.master_accounts.values():
            if existing_master.has_child_account_id(account_id):
                print(f'Account {account_id} already exists as a child account')
                return False

        success = master_account.register_child_account(new_account_info, account_settings, risk_settings)
        if success:
            print(f'Successfully registered child account {account_id}')
        return success
    
    def get_active_master_accounts(self):
        active_master_accounts = []
        for master_account in self.master_accounts.values():
            if master_account.active_copier:
                active_master_accounts.append(master_account)
        return active_master_accounts
    
    def get_master_accounts(self):
        return list(self.master_accounts.values())
    
    def get_child_accounts(self):
        child_accounts = []
        for master_account in self.master_accounts.values():
            for child_account in master_account.child_accounts.values():
                child_accounts.append(child_account)
        return child_accounts
    
    def get_child_accounts_by_master_account(self, master_account):
        return list(master_account.child_accounts.values())

    def get_account(self, account_id):
        """Get account object by ID, whether master or child"""
        if account_id in self.master_accounts:
            return self.master_accounts[account_id]
        for master_account in self.master_accounts.values():
            if master_account.has_child_account_id(account_id):
                return master_account.child_accounts[account_id]
        
        return None
    
    def get_portfolio_value(self):
        total_portfolio_value = 0
        for master_account in self.master_accounts.values():
            if master_account.include_in_portfolio:
                total_portfolio_value += master_account.get_balance()
            for child_account in master_account.child_accounts.values():
                if child_account.include_in_portfolio:
                    total_portfolio_value += child_account.get_balance()
        return total_portfolio_value
    
    def get_account_totals(self):
        master_accounts_total = 0
        child_accounts_total = 0
        master_accounts_total = len(self.master_accounts)
        for master_account in self.master_accounts.values():
            child_accounts_total += len(master_account.child_accounts)
        return master_accounts_total, child_accounts_total
    