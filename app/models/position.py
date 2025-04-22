from app.models.trade import Trade

class Position:
    def __init__(self, instrument):
        self.instrument = instrument
        self.trades = []
        self.trade_ids = {}



    def __str__(self):
        return f"Position in {self.instrument}: {len(self.trades)} open trades"
