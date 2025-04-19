class TradeAccount:
    
    def __init__(self, custom_name, brokerage, account_id, include_in_portfolio : bool):
        self.custom_name : str = custom_name
        self.brokerage = brokerage
        self.account_id : str = account_id
        self.include_in_portfolio : bool = include_in_portfolio
        self.last_transaction_id = ""

    def get_balance(self):
        try:
            account_summary = self.brokerage.get_summary()['account']
            balance = account_summary['balance']
            return float(balance)
        except Exception as e:
            print(f'Error getting balance: {e}')
            return None
        
    def format_balance(self):
        balance = self.get_balance()
        if balance is not None:
            try:
                balance_float = float(balance)
                return "${:,}".format(balance_float)
            except (ValueError, TypeError):
                return "---"
        else:
            return "---"
        
    def get_open_positions(self):
        try:
            open_positions = self.brokerage.get_open_positions()
            return open_positions
        except Exception as e:
            print(f'Error getting open positions: {e}')
            return 0
        
    def get_growth(self):
        try:
            return self.brokerage.get_summary()['account']['pl']
        except Exception as e:
            print(f'Error getting growth: {e}')
            return 0
        
    def get_pending_orders(self):
        try:
            pending_orders = self.brokerage.get_pending_orders()
            return pending_orders
        except Exception as e:
            print(f'Error getting pending orders: {e}')
            return 0
        
    def get_last_transaction_id(self):
        try:
            return self.brokerage.get_summary()['lastTransactionID']
        except Exception as e:
            print(f'Error getting last transaction id: {e}')
            return 0
