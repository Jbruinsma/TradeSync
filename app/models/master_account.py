from app.models.trade_account import TradeAccount
from app.models.child_account import ChildAccount
from app.models.brokerage.oanda_brokerage.oanda import OANDA
from app.models.settings import Settings

class MasterAccount(TradeAccount):
    def __init__(self, custom_name, brokerage, account_id, api_key, is_live, include_in_portfolio):
        super().__init__(custom_name, brokerage, account_id, include_in_portfolio)
        self.active_copier = True
        self.child_accounts = {}
        self.child_account_ids = {}

    def __str__(self):
        return f'{self.custom_name}, {self.account_id}, {self.child_accounts}'

    def register_child_account(self, new_account_info, account_settings, risk_settings):
        try:

            account_id = new_account_info['account_id']
            settings = self._create_settings(account_settings, risk_settings)
            brokerage = self._create_brokerage(new_account_info)

            if self.has_child_account_id(account_id) or account_id == self.account_id:
                return 
            
            child_account = ChildAccount(
                custom_name= account_settings['custom_name'],
                brokerage= brokerage,
                account_id= account_id,
                include_in_portfolio= account_settings['include_in_portfolio'] == "true",
                master_account_id= self.account_id
            )
            child_account.set_settings(settings)
            
            self.child_accounts[account_id] = child_account
            self.child_account_ids[account_id] = True
            return True
            
        except Exception as e:
            print(f'ERROR REGISTERING CHILD ACCOUNT: {e}')
            return False
        
    def has_child_account_id(self, account_id):
        return account_id in self.child_account_ids

    @staticmethod
    def _create_settings(account_settings, risk_settings):
        risk_type = account_settings['risk_type']
        
        if risk_type == 'multiplier':
            return Settings(
                trade_types=account_settings['trade_types'],
                order_types=account_settings['order_types'],
                min_trade_size=account_settings['min_trade_size'],
                max_trade_size=account_settings['max_trade_size'],
                max_open_positions=float('inf') if account_settings['max_open_positions'] is None else account_settings['max_open_positions'],
                risk_type=risk_type,
                multiplier_factor= float(risk_settings['multiplier_factor']),
                fixed_trade_size=float('inf'),
                fixed_stop_loss_size=float('inf'),
                fixed_take_profit_size=float('inf'),
                trade_closure_approach=account_settings['trade_closure']
            )
        elif risk_type == 'fixed':
            return Settings(
                trade_types=account_settings['trade_types'],
                order_types=account_settings['order_types'],
                min_trade_size=account_settings['min_trade_size'],
                max_trade_size=account_settings['max_trade_size'],
                max_open_positions=float('inf') if account_settings['max_open_positions'] is None else account_settings['max_open_positions'],
                risk_type=risk_type,
                multiplier_factor= 1,
                fixed_trade_size=account_settings['fixed_trade_size'],
                fixed_stop_loss_size=account_settings['fixed_stop_loss_size'],
                fixed_take_profit_size=account_settings['fixed_take_profit_size'],
                trade_closure_approach=account_settings['trade_closure']
            )

    def _create_master_account(self, new_account_info, settings):
        brokerage = self._create_brokerage(new_account_info)
        return MasterAccount(
            custom_name=settings.custom_name.data,
            brokerage=brokerage,
            account_id=new_account_info['account_id'],
            api_key=new_account_info['api_key'],
            is_live=new_account_info['account_type'] == 'live',
            include_in_portfolio=settings.include_in_portfolio.data == "true"
        )
    @staticmethod
    def _create_brokerage(account_info):
        if account_info['brokerage'] == 'oanda':
            return OANDA(
                account_id=account_info['account_id'],
                api_key=account_info['api_key'],
                is_live=account_info['account_type'] == 'live'
            )
        raise ValueError(f"Unsupported brokerage: {account_info['brokerage']}")