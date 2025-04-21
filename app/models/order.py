from app.models.base_order import BaseOrder


class Order(BaseOrder):
    def __init__(self, parent_order_id, order_id, instrument, units, order_type, price, stop_loss=None, take_profit=None):
            super().__init__(parent_order_id, order_id, instrument, units, stop_loss, take_profit)
            self.order_type = order_type
            self.price = price

    def __str__(self):
        return (f"Order: parent_order_id: {self.parent_order_id}, order_id: {self.order_id}, instrument: {self.instrument}, units: {self.units},"
                f" order_type: {self.order_type}, price: {self.price}, stop_loss: {self.stop_loss}, take_profit: {self.take_profit})")
    
    def compare(self, order_dict) -> dict:
        """
        Compare this order with a dictionary representation of an order
        
        Args:
            order_dict (dict): Dictionary containing order details
            
        Returns:
            dict: Dictionary of differences found, empty if no differences
        """
        differences = {}
        
        try:
            # Required fields
            required_fields = {
                'id': 'order_id',
                'instrument': 'instrument',
                'units': 'units',
                'type': 'order_type',
                'price': 'price'
            }
            
            # Check required fields
            for api_field, attr_name in required_fields.items():
                if api_field not in order_dict:
                    differences[attr_name] = f"Missing required field: {api_field}"
                    continue
                    
                current_value = getattr(self, attr_name)
                new_value = order_dict[api_field]
                
                if current_value != new_value:
                    differences[attr_name] = {
                        'current': current_value,
                        'new': new_value
                    }
            
            # Optional fields
            if 'stopLossOnFill' in order_dict:
                new_stop_loss = order_dict['stopLossOnFill']['price']
                if self.stop_loss != new_stop_loss:
                    differences['stop_loss'] = {
                        'current': self.stop_loss,
                        'new': new_stop_loss
                    }
                    
            if 'takeProfitOnFill' in order_dict:
                new_take_profit = order_dict['takeProfitOnFill']['price']
                if self.take_profit != new_take_profit:
                    differences['take_profit'] = {
                        'current': self.take_profit,
                        'new': new_take_profit
                    }
                    
        except Exception as e:
            differences['error'] = f"Error comparing orders: {str(e)}"
            
        return differences
    
    def update_from_dict(self, order_dict) -> bool:
        """
        Update this order's attributes from a dictionary
        
        Args:
            order_dict (dict): Dictionary containing order details
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            differences = self.compare(order_dict)
            if not differences:
                return True
                
            # Update only changed fields
            for field, value in differences.items():
                if isinstance(value, dict):
                    setattr(self, field, value['new'])
                    
            return True
            
        except Exception as e:
            print(f"Error updating order: {str(e)}")
            return False
