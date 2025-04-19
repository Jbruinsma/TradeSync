class Settings:

    def __init__(self, trade_types, order_types, min_trade_size, max_trade_size, max_open_positions, risk_type, multiplier_factor, fixed_trade_size, fixed_stop_loss_size, fixed_take_profit_size, trade_closure_approach):
        self.trade_types = self._get_trade_types_dict(trade_types)
        self.order_types = self._get_order_types_dict(order_types)
        self.min_trade_size = min_trade_size
        self.max_trade_size = max_trade_size
        self.max_open_positions = max_open_positions
        self.risk_type = risk_type
        self.multiplier_factor = multiplier_factor
        self.fixed_trade_size = fixed_trade_size
        self.fixed_stop_loss_size = fixed_stop_loss_size
        self.fixed_take_profit_size = fixed_take_profit_size
        self.trade_closure_approach = trade_closure_approach

    def __str__(self):
        return (f'Trade Types: {self.trade_types}, Order Types: {self.order_types}, Min Trade Size: {self.min_trade_size},'
                f'Max Trade Size: {self.max_trade_size}, Max Open Positions: {self.max_open_positions},'
                f'Risk Type: {self.risk_type}, Multiplier Factor: {self.multiplier_factor}, '
                f'Fixed Trade Size: {self.fixed_trade_size}, Fixed Stop Loss(pips): {self.fixed_stop_loss_size}, '
                f'Fixed Take Profit(pips): {self.fixed_take_profit_size}, Trade Closure Approach: {self.trade_closure_approach}')

    @staticmethod
    def _get_trade_types_dict(trade_types):
        trade_types = {
            'all': trade_types[0],
            'buy': trade_types[1],
            'sell': trade_types[2]
        }

        if not trade_types['buy'] and not trade_types['sell']:
            trade_types['all'] = True
        print(f'TRADE TYPES: {trade_types}')
        return trade_types

    @staticmethod
    def _get_order_types_dict(order_types):
        order_types = {
            'all': order_types[0],
            'market': order_types[1],
            'limit': order_types[2],
            'stop': order_types[3]
        }

        if not order_types['market'] and not order_types['limit'] and not order_types['stop']:
            order_types['all'] = True
        print(f'ORDER TYPES: {order_types}')
        return order_types
