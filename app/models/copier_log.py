class CopierLog:

    def __init__(self, status, master_account_name, child_account_name, trade_type, trade_size, open_time, close_time, open_price, close_price, pl):
        self.status = status
        self.master_account_name = master_account_name
        self.child_account_name = child_account_name
        self.trade_type = trade_type
        self.trade_size = trade_size
        self.open_time = open_time
        self.close_time = close_time
        self.open_price = open_price
        self.close_price = close_price
        self.pl = pl

    def to_dict(self):
        return {'status': self.status,
                'masterAccountName': self.master_account_name,
                'childAccountName': self.child_account_name,
                'tradeType': self.trade_type,
                'tradeSize': self.trade_size,
                'openTime': self.open_time,
                'closeTime': self.close_time,
                'openPrice': self.open_price,
                'closePrice': self.close_price,
                'pl': self.pl}
