from app.models.base_order import BaseOrder


class Trade(BaseOrder):
    def __init__(self, parent_order_id, order_id, instrument, units, state, stop_loss=None, take_profit=None):
        super().__init__(parent_order_id, order_id, instrument, units, stop_loss, take_profit)
        self.state = state

    def __str__(self):
        return f"Parent order id: {self.parent_order_id}, order_id: {self.order_id}, instrument: {self.instrument}, units: {self.units}, state: {self.state}, stop_loss: {self.stop_loss}, take_profit: {self.take_profit}"
