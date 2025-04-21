class BaseOrder:
    def __init__(self, parent_order_id, order_id, instrument, units, stop_loss=None, take_profit=None):
        self.parent_order_id = parent_order_id
        self.order_id = order_id
        self.instrument = instrument
        self.units = units
        self.stop_loss = stop_loss
        self.take_profit = take_profit