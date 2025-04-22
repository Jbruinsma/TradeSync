import math

from app.models.brokerage.oanda_brokerage.pip_sizes import PIP_SIZES
from app.models.encryption import CredentialEncryption
from app.models.brokerage.brokerage import Brokerage
from app.models.order import Order

import requests

from app.models.position import Position
from app.models.trade import Trade


class OANDA(Brokerage):

    def __init__(self, account_id, api_key, is_live):
        super().__init__()
        self.account_state = {}
        self.account_id = account_id
        self.credential_encryption = CredentialEncryption()
        self.encrypted_api_key = self.credential_encryption.encrypt_api_key(api_key)
        
        if is_live:
            self.base_url = "https://api-fxtrade.oanda.com"
        else:
            self.base_url = "https://api-fxpractice.oanda.com"

    def __del__(self):
        self.encrypted_api_key = None

    @property
    def headers(self):
        """Generate headers on-demand with decrypted API key"""
        decrypted_key = self.credential_encryption.decrypt_api_key(self.encrypted_api_key)
        headers = {
            "Authorization": f"Bearer {decrypted_key}",
            "Content-Type": "application/json"
        }
        del decrypted_key
        return headers

    def get_summary(self):
        endpoint = f"/v3/accounts/{self.account_id}/summary"
        return self._make_request(method= "GET", endpoint= endpoint)

    def get_account_type(self):
        if self.base_url == "https://api-fxtrade.oanda.com":
            return "Live"
        else:
            return "Demo"

    def get_api_key(self):
        return self.credential_encryption.decrypt_api_key(self.encrypted_api_key)

    def get_open_positions(self):
        try:
            summary = self.get_summary()['account']
            return summary['openPositionCount']
        except Exception as e:
            print(f'Error getting open positions: {e}')
            return 0

    def create_order(self, parent_order):
        endpoint = f"/v3/accounts/{self.account_id}/orders"
        print(f"PARENT ORDER: {parent_order}")

        parent_order_id = parent_order['id']

        order = {
            "order": {
                "type": parent_order['type'],
                "instrument": parent_order['instrument'],
                "units": str(parent_order['units']),
                "positionFill": "DEFAULT"
            }
        }

        if parent_order['type'] in ["LIMIT", "STOP"] and parent_order.get('price') is not None:
            order["order"]["price"] = str(parent_order['price'])

        if "stopLossOnFill" in parent_order:
            order["order"]["stopLossOnFill"] = {
                "price": str(parent_order['stopLossOnFill']['price'])
            }

        if "takeProfitOnFill" in parent_order:
            order["order"]["takeProfitOnFill"] = {
                "price": str(parent_order['takeProfitOnFill']['price'])
            }

        final_order = self._format_order_details(order)
        print(f"FINAL ORDER: {final_order}")

        if final_order is None:
            print("ORDER REJECTED BECAUSE OF CHILD ACCOUNT SETTINGS!")
            return None

        try:
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=final_order
            )
            print(f"(Line 103 in oanda.py) FULL RESPONSE: {response}")
            order_create_transaction = response['orderCreateTransaction']
            order_fill_transaction = response['orderFillTransaction']
            if order_fill_transaction:
                new_position = self.format_new_trade(parent_order_id= parent_order_id, order= order_fill_transaction)
                print(f"(LINE 108 in oanda.py) NEW POSITION: {new_position}")
                self.current_positions[str(new_position.parent_order_id)] = new_position
            else:
                new_order = self.format_new_order(parent_order_id= parent_order_id, api_response= order_create_transaction)
                print(f"(LINE 112 in oanda.py) NEW ORDER: {new_order}")
                self.current_orders[str(new_order.parent_order_id)] = new_order

            return response

        except Exception as e:
            print(f"Error creating order: {e}")
            raise

    def modify_order(self, order_id, new_order_details):
        """
        Modify an existing order with new details.

        Args:
            order_id (str): The child order's ID.
            new_order_details (dict): The modified order payload.

        Returns:
            dict: Response from the API.
        """
        endpoint = f"/v3/accounts/{self.account_id}/orders/{order_id}"
        try:
            response = self._make_request(method="PUT", endpoint=endpoint, data=new_order_details)
            return response
        except Exception as e:
            print(f"Error modifying order {order_id}: {e}")
            raise

    def update_trade_orders(self, trade_id, stop_loss=None, take_profit=None):
        """
        Update the stop loss and/or take profit orders for an open trade.

        Args:
            trade_id (str): The ID of the open trade.
            stop_loss (str or float, optional): The new stop loss price.
            take_profit (str or float, optional): The new take profit price.

        Returns:
            dict: The API response from OANDA.
        """
        endpoint = f"/v3/accounts/{self.account_id}/trades/{trade_id}/orders"
        payload = self._format_trade_order_settings(stop_loss, take_profit)

        try:
            response = self._make_request(method="PUT", endpoint=endpoint, data=payload)
            print(f"Trade {trade_id} orders updated: {response}")
            return response
        except Exception as e:
            print(f"Error updating trade orders for trade {trade_id}: {e}")
            raise

    def get_account_changes(self, transaction_id="0"):
        endpoint = f"/v3/accounts/{self.account_id}/changes"
        params = {"sinceTransactionID": transaction_id}

        try:
            response = self._make_request(method="GET", endpoint=endpoint, params=params)
            changes = response["changes"]
            last_transaction_id = response["lastTransactionID"]

            return {"changes": changes, "last_transaction_id": last_transaction_id}
        except Exception as e:
            print(f"Error getting account changes: {e}")
            return None

    def cancel_order(self, parent_order_id):
        if parent_order_id not in self.current_orders:
            print('ORDER NOT FOUND')
            return
        else:
            order = self.current_orders[parent_order_id]
            order_id = order.order_id

        endpoint = f"/v3/accounts/{self.account_id}/orders/{order_id}/cancel"
        try:
            response = self._make_request(method="PUT", endpoint=endpoint)
            print(f"(LINE 153 in oanda.py) CANCELLATION RESPONSE: {response}")
            print("(LINE 154 in oanda.py) self.current_orders: {", self.current_orders, "}")
            if "orderCancelTransaction" in response:
                del self.current_orders[parent_order_id]
            print("(LINE 157 in oanda.py) self.current_orders: {", self.current_orders, "}")
            return response
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")
            return None

    def close_open_trade(self, trade_id, units):
        endpoint = f"/v3/accounts/{self.account_id}/trades/{trade_id}/close"
        data = {}
        if units is not None:
            data["units"] = units
        try:
            response = self._make_request(method="PUT", endpoint=endpoint, data=data)
            return response
        except Exception as e:
            print(f"Error closing order {trade_id}: {e}")
            raise

    def get_open_trades(self):
        """
        Get all currently open trades

        Returns:
            dict: List of open trades with details
        """
        endpoint = f"/v3/accounts/{self.account_id}/openTrades"

        try:
            response = self._make_request(
                method="GET",
                endpoint=endpoint
            )
            return response
        except Exception as e:
            print(f"Error getting open trades: {e}")
            raise

    def get_pending_orders(self):
        """
        Get all pending orders (not yet executed)

        Returns:
            dict: List of pending orders
        """
        endpoint = f"/v3/accounts/{self.account_id}/pendingOrders"

        try:
            response = self._make_request(
                method="GET",
                endpoint=endpoint
            )
            return response
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            raise

    def get_current_transaction_id(self):
        """Get the current transaction ID for the account"""
        try:
            response = self.get_summary()
            return response['account']['lastTransactionID']
        except Exception as e:
            print(f"Error getting current transaction ID: {e}")
            raise

    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make a request to the OANDA API

        Args:
            method (str): HTTP method (GET, POST, PUT, etc.)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body data

        Returns:
            dict: Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to OANDA API: {e}")
            raise

    @staticmethod
    def _compare_order_changes(old_order, new_order):
        important_keys = ["price", "units", "timeInForce", "gtdTime", "triggerCondition"]
        changes = {}
        for key in important_keys:
            old_value = old_order.get(key)
            new_value = new_order.get(key)
            if old_value != new_value:
                changes[key] = {"from": old_value, "to": new_value}
        old_sl = old_order.get("stopLossOnFill", {}).get("price")
        new_sl = new_order.get("stopLossOnFill", {}).get("price")
        if old_sl != new_sl:
            changes["stopLoss"] = {"from": old_sl, "to": new_sl}
        return changes

    def _handle_order_modifications(self, changes):
        cancelled_orders = changes.get("ordersCancelled", [])
        created_orders = changes.get("ordersCreated", [])

        # Build a mapping of replaced orders
        replacements = {
            o.get("replacesOrderID"): o
            for o in created_orders
            if "replacesOrderID" in o
        }

        for old_order in cancelled_orders:
            new_order = replacements.get(old_order["id"])
            if new_order:
                diff = self._compare_order_changes(old_order, new_order)
                if diff:
                    print(f"Order modified: {diff}")

    def _format_order_details(self, order):
        base_order = order["order"]
        settings = self.settings
        risk_type = settings.risk_type
        trade_size = float(base_order['units'])
        instrument = base_order['instrument']
        is_buy = trade_size > 0
        is_sell = trade_size < 0

        print(f'CHILD ACCOUNT SETTINGS: {self.settings}')

        if not settings.trade_types["all"]:
            if is_buy and not settings.trade_types["buy"]:
                return None
            if is_sell and not settings.trade_types["sell"]:
                return None

        order_type = base_order["type"].lower()

        if risk_type == "fixed_lot":
            new_trade_size = settings.fixed_trade_size
            new_trade_size = new_trade_size if is_buy else -new_trade_size
        else:
            scaled_size = trade_size * float(settings.multiplier_factor)
            if settings.min_trade_size is not None and settings.max_trade_size is not None:
                new_trade_size = max(settings.min_trade_size, min(settings.max_trade_size, abs(scaled_size)))
            else:
                new_trade_size = abs(scaled_size)
            new_trade_size = new_trade_size if is_buy else -new_trade_size
            base_order['units'] = str(round(new_trade_size))

            if risk_type == "fixed_lot" and settings.fixed_stop_loss_size is not None:
                ref_price = float(base_order.get("price", 0))
                new_sl_price = self._calculate_price(ref_price, float(settings.fixed_stop_loss_size), is_buy,
                                                     instrument, "SL")
                base_order['stopLossOnFill'] = {"price": new_sl_price}

            if risk_type == "fixed_lot" and settings.fixed_take_profit_size is not None:
                ref_price = float(base_order.get("price", 0))
                new_tp_price = self._calculate_price(ref_price, float(settings.fixed_take_profit_size), is_buy,
                                                     instrument, "TP")
                base_order['takeProfitOnFill'] = {"price": new_tp_price}

            return {"order": base_order}

    @staticmethod
    def format_new_order(parent_order_id, api_response):
        print(f"API RESPONSE: {api_response}")
        child_order_id = api_response['id']
        instrument = api_response['instrument']
        units = api_response['units']
        order_type = api_response['type']
        price = api_response['price']
        if "takeProfitOnFill" in api_response:
            take_profit_price = api_response['takeProfitOnFill']['price']
        else:
            take_profit_price = None
        if "stopLossOnFill" in api_response:
            stop_loss_price = api_response['stopLossOnFill']['price']
        else:
            stop_loss_price = None
        new_order = Order(parent_order_id= parent_order_id,
                          order_id= child_order_id,
                          instrument= instrument,
                          units= units,
                          order_type= order_type,
                          price= price,
                          stop_loss= stop_loss_price,
                          take_profit= take_profit_price
                          )
        return new_order

    @staticmethod
    def format_new_trade(parent_order_id, order):
        print(f"(Line 384 in oanda.py) Order: {order}")
        order_id = order['id']
        instrument = order['instrument']
        units = order['units']
        state = "FILLED"
        if "stopLossOnFill" in order:
            stop_loss = order['stopLossOnFill']
        else:
            stop_loss = None
        if "takeProfitOnFill" in order:
            take_profit = order['takeProfitOnFill']
        else:
            take_profit = None
        return Trade(parent_order_id= parent_order_id,
                     order_id= order_id,
                     instrument= instrument,
                     units= units,
                     state= state,
                     stop_loss= stop_loss,
                     take_profit= take_profit)

    @staticmethod
    def _calculate_price(base_price, pips, is_buy, instrument, price_type):
        base_price = float(base_price)
        pip_value = PIP_SIZES.get(instrument, 0.0001)
        adjusted_price = pips * pip_value

        if price_type.upper() == "SL":
            new_price = base_price - adjusted_price if is_buy else base_price + adjusted_price
        elif price_type.upper() == "TP":
            new_price = base_price + adjusted_price if is_buy else base_price - adjusted_price
        else:
            raise ValueError("price_type must be either 'SL' or 'TP'")

        decimals = abs(int(round(math.log10(pip_value))))
        new_price = round(new_price, decimals)
        return str(new_price)

    @staticmethod
    def _format_trade_order_settings(stop_loss=None, take_profit=None):
        """
        Format the stop loss and take profit settings for an open trade.

        Args:
            stop_loss (str or float, optional): The stop loss price to set.
            take_profit (str or float, optional): The take profit price to set.

        Returns:
            dict: A dictionary with the formatted 'stopLoss' and/or 'takeProfit' settings.
        """
        settings = {}

        if stop_loss is not None:
            settings["stopLoss"] = {
                "timeInForce": "GTC",  # Good 'Til Cancelled, adjust if needed.
                "price": str(stop_loss)
            }

        if take_profit is not None:
            settings["takeProfit"] = {
                "timeInForce": "GTC",  # Good 'Til Cancelled, adjust if needed.
                "price": str(take_profit)
            }

        return settings
