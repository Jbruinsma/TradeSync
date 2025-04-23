import asyncio
from typing import Dict, Optional

from app import user_db
from app.models.brokerage.oanda_brokerage.oanda import OANDA
from app.models.order import Order
from app.models.trade import Trade


class TradeCopier:

    def __init__(self):
        self.order_mappings = {}
        self.trade_mappings = {}
        self.last_transaction_ids = {}
        self.status = "idle"
        self.users = user_db.inorder_traversal()

    def start(self):
        self.status = "active"

    def stop(self):
        self.status = "idle"

    def update(self):
        self.users = user_db.inorder_traversal()

    async def run(self):
        # Main loop that runs the trade copier functionalities.
        while self.status == "active":
            await self.iterate_users()

    async def iterate_users(self):
        # Iterates through a sorted array of User objects that contain master accounts.
        for user in self.users:
            await self.iterate_master_accounts(user)

    async def iterate_master_accounts(self, user):
        # Iterates through the MasterAccount Objects stored in the User object to check if a change has been made (Trade
        # Placed, Canceled, modified, etc.). MasterAccounts are stored in a dictionary.
        for master_account in user.master_accounts.values():
            if not master_account.active_copier:
                continue

            # Get the current transaction ID if we don't have one
            if master_account.account_id not in self.last_transaction_ids:
                try:
                    current_id = master_account.brokerage.get_current_transaction_id()
                    self.last_transaction_ids[master_account.account_id] = current_id
                except Exception as e:
                    print(f"Error getting current transaction ID: {e}")
                    continue

            # Get changes since the last processed transaction
            last_id = self.last_transaction_ids.get(master_account.account_id)
            try:
                changes = master_account.brokerage.get_account_changes(last_id)
            except Exception as e:
                print(f"Error getting account changes: {e}")
                continue
            
            if not changes:
                continue

            # Update last processed transaction ID
            self.last_transaction_ids[master_account.account_id] = changes["last_transaction_id"]

            # Process changes for each child account
            for child_account in master_account.child_accounts.values():
                await self.handle_account_changes(child_account.brokerage, changes["changes"])

    async def handle_account_changes(self, child_account: OANDA, changes: Dict):
        """Handle different types of changes in the master account"""

        # 1) New Orders
        for order in changes.get("ordersCreated", []):
            if "replacesOrderID" not in order:
                await self.handle_new_order(child_account, order)

        # 2) Cancellations (either replacements or pure cancellations)
        for order in changes.get("ordersCancelled", []):
            if "replacedByOrderID" in order:
                # this is an order‐modification flow (including TP/SL additions)
                await self.handle_order_modification(child_account, order, changes)
            else:
                # pure cancellation
                await self.handle_order_cancellation(child_account, order)

        # 3) Fills
        for order in changes.get("ordersFilled", []):
            await self.handle_order_fill(child_account, order)

        # 4) Trade closures
        for trade in changes.get("tradesClosed", []):
            await self.handle_trade_closure(child_account, trade)

        # 5) SL/TP added after market fills
        for order in changes.get("ordersCreated", []):
            if order["type"] in ["TAKE_PROFIT", "STOP_LOSS"] and "tradeID" in order:
                await self.handle_post_fill_sl_tp_order(child_account, order)

    async def handle_new_order(self, child_account: OANDA, order: Dict):
        try:
            response = child_account.create_order(order)
            if not response:
                return

            # Store mapping between master and child orders
            self.order_mappings[order["id"]] = response["orderCreateTransaction"]["id"]

            # If order was immediately filled, store trade mapping
            fill_tx = response.get("orderFillTransaction")
            if fill_tx:
                self.trade_mappings[order["id"]] = fill_tx["tradeOpened"]["id"]

        except Exception as e:
            print(f"Error creating order on child account: {e}")

    async def handle_order_modification(self, child_account: OANDA, old_order: Dict, changes: Dict):
        """
        Handle modifications to existing orders (replacements, including TP/SL additions).
        """
        master_order_id = old_order["id"]
        new_order_id = old_order["replacedByOrderID"]

        # Do we have a child order for this master ID?
        if master_order_id not in self.order_mappings:
            return

        try:
            # 1) Cancel the old order on the child (pass master_order_id so cancel_order
            #    finds it in current_orders and then uses its .order_id internally)
            child_account.cancel_order(master_order_id)

            # 2) Remove our mapping for that old master order
            del self.order_mappings[master_order_id]

            # 3) Find the replacement in this batch of changes
            new_order = next(
                (o for o in changes.get("ordersCreated", []) if o["id"] == new_order_id),
                None
            )

            # 4) Re-create it (with any added SL/TP) on the child
            if new_order:
                await self.handle_new_order(child_account, new_order)

        except Exception as e:
            print(f"Error modifying order on child account: {e}")
    async def handle_order_fill(self, child_account: OANDA, order: Dict):
        """Handle when an order is filled"""
        # For market orders, this is handled in handle_new_order
        if order["type"] == "MARKET":
            return

        # For limit/stop orders, we need to handle the fill
        child_order_id = self.order_mappings.get(order["id"])
        if not child_order_id:
            return

        try:
            # The broker should fill the child order automatically.
            # We just need to update our mappings
            if "tradeOpenedID" in order:
                self.trade_mappings[order["id"]] = order["tradeOpenedID"]
        except Exception as e:
            print(f"Error handling order fill on child account: {e}")

    async def handle_trade_closure(self, child_account: OANDA, trade: Dict):
        """Handle closing of trades"""
        child_trade_id = self.trade_mappings.get(trade["id"])
        if not child_trade_id:
            return

        try:
            # Close the trade on child account
            child_account.close_open_trade(child_trade_id, None)
            
            # Remove mappings
            del self.trade_mappings[trade["id"]]
            if trade.get("takeProfitOrderID") in self.order_mappings:
                del self.order_mappings[trade["takeProfitOrderID"]]
            if trade.get("stopLossOrderID") in self.order_mappings:
                del self.order_mappings[trade["stopLossOrderID"]]
        except Exception as e:
            print(f"Error closing trade on child account: {e}")

    async def handle_post_fill_sl_tp_order(self, child_account: OANDA, order: Dict):
        trade_id = order.get("tradeID")
        if not trade_id:
            return
        child_trade_id = self.trade_mappings.get(trade_id)
        if not child_trade_id:
            return

        sl = order["price"] if order["type"] == "STOP_LOSS" else None
        tp = order["price"] if order["type"] == "TAKE_PROFIT" else None

        try:
            await asyncio.sleep(0.5)  # Slight delay can help ensure trade is open
            child_account.update_trade_orders(child_trade_id, stop_loss=sl, take_profit=tp)
        except Exception as e:
            print(f"Error applying SL/TP to trade {child_trade_id}: {e}")

    async def handle_order_cancellation(self, child_account: OANDA, order: Dict):
        """
        Handle a master-side LIMIT/STOP order being cancelled outright
        (not as part of a replace).
        """
        master_order_id = order["id"]
        # Do we know a child order for this master order?
        if master_order_id not in self.order_mappings:
            return

        try:
            # OANDA.cancel_order expects the master_order_id as the key into current_orders
            child_account.cancel_order(master_order_id)
            print(f"[TC] Cancelled child order for master {master_order_id}")
        except Exception as e:
            print(f"Error cancelling order on child account: {e}")
        finally:
            # Clean up our mapping
            del self.order_mappings[master_order_id]