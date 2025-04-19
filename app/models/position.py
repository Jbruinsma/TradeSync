class Position:

    def __init__(self, parent_order_id, order_id, instrument, units, state, stop_loss= None, take_profit= None):
        self.parent_order_id = parent_order_id
        self.order_id = order_id
        self.instrument = instrument
        self.units = units
        self.state = state
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def __str__(self):
        return f"Parent order id: {self.parent_order_id}, order_id: {self.order_id}, instrument: {self.instrument}, units: {self.units}, state: {self.state}, stop_loss: {self.stop_loss}, take_profit: {self.take_profit}"