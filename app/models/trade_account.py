from app.models.brokerage.oanda_brokerage.oanda import OANDA
from app.models.queue.queue import ProfitQueue


class TradeAccount:
    
    def __init__(self, custom_name: str, brokerage: OANDA, account_id : str, include_in_portfolio : bool, account_summary : dict):
        self.custom_name : str = custom_name
        self.brokerage : OANDA = brokerage
        self.account_id : str = account_id
        self.include_in_portfolio : bool = include_in_portfolio
        self.last_transaction_id : str = ""

        self.meta : dict = account_summary # {'balance': int, 'currency': str, 'pl': str, 'OpenTradeCount': str, 'openPositionCount': str, 'pendingOrderCount': str, 'lastTransactionID': str}
        self.profits = {'month': ProfitQueue(), 'week': ProfitQueue(), 'day': 0}

    def get_account_summary(self) -> dict:
        return self.meta

    def get_balance(self) -> float:
        return float(self.meta['balance'])
        
    def format_balance(self) -> str:
        balance = self.get_balance()
        if balance is not None:
            try:
                balance_float = float(balance)
                return "${:,}".format(balance_float)
            except (ValueError, TypeError):
                return "---"
        else:
            return "---"
        
    def get_open_positions(self) -> int:
        return int(self.meta['openPositionCount'])
        
    def get_growth(self) -> float:
        return float(self.meta['pl'])

    def get_pending_order_count(self) -> int:
        return int(self.meta['pendingOrderCount'])

    def get_pending_orders(self) -> dict | int:
        try:
            pending_orders = self.brokerage.get_pending_orders()
            return pending_orders
        except Exception as e:
            print(f'Error getting pending orders: {e}')
            return 0
        
    def get_last_transaction_id(self) -> str:
        return self.meta['lastTransactionID']

    def update_meta_balance(self, balance) -> None:
        self.meta['balance'] = balance

    def update_meta_pl(self, pl) -> None:
        self.meta['pl'] = pl

    def update_meta_open_trade_count(self, open_trade_count) -> None:
        self.meta['openTradeCount'] = open_trade_count

    def update_meta_open_position_count(self, open_position_count) -> None:
        self.meta['openPositionCount'] = open_position_count

    def update_meta_pending_order_count(self, pending_order_count) -> None:
        self.meta['pendingOrderCount'] = pending_order_count

    def update_meta_last_transaction_id(self, last_transaction_id) -> None:
        self.meta['lastTransactionID'] = last_transaction_id