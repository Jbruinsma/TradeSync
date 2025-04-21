# position.py
from trade import Trade

class Position:
    def __init__(self, instrument):
        self.instrument = instrument
        self.trades = []
        self.trade_ids = {}

    def add_trade(self, trade: Trade):
        if trade.instrument == self.instrument:
            self.trades.append(trade)

    def remove_trade_by_id(self, order_id):
        self.trades = [t for t in self.trades if t.order_id != order_id]

    def __str__(self):
        return f"Position in {self.instrument}: {len(self.trades)} open trades"
