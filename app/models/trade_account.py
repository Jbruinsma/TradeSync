class TradeAccount:
    
    def __init__(self, custom_name, brokerage, account_id, include_in_portfolio : bool, account_summary):

        self.custom_name : str = custom_name
        self.brokerage = brokerage
        self.account_id : str = account_id
        self.include_in_portfolio : bool = include_in_portfolio
        self.last_transaction_id = ""
        self.meta = account_summary # {'balance': int, 'currency': str, 'pl': str, 'OpenTradeCount': str, 'openPositionCount': str, 'pendingOrderCount': str, 'lastTransactionID': str}

    def get_account_summary(self):
        return self.meta

    def get_balance(self):
        return float(self.meta['balance'])
        
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
        return self.meta['openPositionCount']
        
    def get_growth(self):
        return self.meta['pl']

    def get_pending_order_count(self):
        return self.meta['pendingOrderCount']

    def get_pending_orders(self):
        try:
            pending_orders = self.brokerage.get_pending_orders()
            return pending_orders
        except Exception as e:
            print(f'Error getting pending orders: {e}')
            return 0
        
    def get_last_transaction_id(self):
        return self.meta['lastTransactionID']