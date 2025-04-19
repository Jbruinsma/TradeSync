from app import user_db
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_second=2):
        self.requests_per_second = requests_per_second
        self.request_history = defaultdict(list)

    def can_make_request(self, account_id: str) -> bool:
        """
        Check if we can make a request for this account based on rate limits
        """
        now = datetime.now()
        # Clean up old requests (older than 1 second)
        self.request_history[account_id] = [
            timestamp for timestamp in self.request_history[account_id]
            if now - timestamp < timedelta(seconds=15)
        ]
        
        # Check if we've made too many requests in the last second
        return len(self.request_history[account_id]) < self.requests_per_second

    def add_request(self, account_id: str):
        """Record that a request was made"""
        self.request_history[account_id].append(datetime.now())

    async def wait_if_needed(self, account_id: str):
        """
        Wait until we can make another request if we're at the rate limit
        """
        while not self.can_make_request(account_id):
            await asyncio.sleep(0.1)
        self.add_request(account_id)

class TradeCopier:

    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.last_poll_time = datetime.now()
        self.poll_interval = timedelta(seconds=30)
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

    async def process_users(self):
        print("TRADE COPIER WORKING: Status:", self.status)
        while self.status == "active" and len(self.users) > 0:
            for i in range(len(self.users)):
                user = self.users[i]
                await self.process_user(user)
            await asyncio.sleep(1)

    async def process_user(self, user):
        master_accounts = user.get_active_master_accounts()
        for master_account in master_accounts:
            try:
                if master_account.account_id not in self.last_transaction_ids:
                    current_transaction_id = master_account.brokerage.get_current_transaction_id()
                    self.last_transaction_ids[master_account.account_id] = current_transaction_id
                    print(f"Initialized transaction ID for {master_account.account_id}: {current_transaction_id}")
                    continue

                last_transaction_id = self.last_transaction_ids[master_account.account_id]
                result = master_account.brokerage.get_account_changes(last_transaction_id)

                if result:
                    changes = result["changes"]
                    # This is where you trigger your helper method:
                    await self.process_child_accounts(master_account, changes)

                    # Update the last transaction ID for the next poll:
                    self.last_transaction_ids[master_account.account_id] = result["last_transaction_id"]

            except Exception as e:
                print(f"Error processing user {user.username}: {e}")

    async def process_child_accounts(self, master_account, changes):
        print(f"CHANGE: {changes}")
        orders_created = changes.get("ordersCreated", [])
        orders_cancelled = changes.get("ordersCancelled", [])
        orders_filled = changes.get("ordersFilled", [])
        trades_opened = changes.get("tradesOpened", [])
        trades_closed = changes.get("tradesClosed", [])
        # 1) Handle newly created orders
        for order in orders_created:
            order_type = order.get("type", "")
            # Check if this is a replacement for an older order
            replaced_id = order.get("replacesOrderID")

            if replaced_id:
                # This is a modification replacing an old order
                # You can pass both the old order ID and the new order data
                print(f"Order {replaced_id} was replaced by {order['id']}")
                # If you want, call your “process_order_modification”
                await self.process_order_modification(
                    original_parent_order_id= replaced_id,  # or your own mapping
                    master_account=master_account,
                    change=order
                )
            else:
                # Normal newly-created order
                if order_type == "MARKET":
                    # e.g. an immediate Market order
                    print("Detected MARKET order creation.")
                    await self.process_market_order(master_account, order)
                elif "LIMIT" in order_type or "STOP" in order_type:
                    # A pending Limit/Stop order
                    print("Detected LIMIT or STOP order creation.")
                    await self.process_new_order(master_account, order)
                elif "TAKE_PROFIT" in order_type or "STOP_LOSS" in order_type:
                    # An attached TP/SL order
                    print("Detected attached SL or TP creation.")
                    # Possibly a call to update an existing trade’s SL/TP
                    await self.process_trade_order_update(master_account, order)
                else:
                    print(f"Unrecognized order creation type: {order_type}")
                    # Handle as needed
        # 2) Handle cancelled orders
        for order in orders_cancelled:
            print(f"Detected cancelled order: {order.get('id')}")
            await self.process_order_cancellations(master_account, order)

        # 3) Handle filled orders
        #(These are orders that just got executed into an open trade.)
        for order in orders_filled:
            order_type = order.get("type", "")
            if order_type == "MARKET":
                # A Market order that got filled
                print(f"Detected filled MARKET order: {order.get('id')}")
                await self.process_market_order(master_account, order)
            elif "LIMIT" in order_type or "STOP" in order_type:
                # A Limit or Stop order that got filled -> new position
                print(f"Detected filled LIMIT/STOP order: {order.get('id')}")
                await self.process_market_order(master_account, order)
            else:
                print(f"Unrecognized filled order type: {order_type}")
                # Handle as needed

        # 4) Handle newly opened trades
        #    (E.g. "tradesOpened" often complements an ordersFilled event)
        for trade in trades_opened:
            print(f"Detected opened trade: {trade.get('id')}")
            # Possibly link up the master-trade -> child-trade
            # Or call your existing process_trade_order_update

        # 5) Handle closed trades
        for trade in trades_closed:
            trade_id = trade.get("id")
            print(f"Detected closed trade: {trade_id}")
            # If you want to replicate closing the trade on child accounts:
            # (Though the user’s code might close it automatically)
            # E.g.: self.process_trade_closure(...)

    async def process_order_modification(self, original_parent_order_id, master_account, change):
        print("ORDER WILL BE MODIFIED")
        # Retrieve the child order ID from the TradeCopier's order mapping.
        child_order_id = self.order_mappings.get(original_parent_order_id)
        if not child_order_id:
            print("Child order mapping not found; falling back to cancel and recreate.")
            cancelled_order = {"orderID": original_parent_order_id}
            await self.process_order_cancellations(master_account, cancelled_order)
            await self.process_new_order(master_account, change)
            return

        # Build the new payload (only include modified fields like stop loss or take profit)
        new_payload = {}
        if "stopLossOnFill" in change:
            new_payload["stopLossOnFill"] = {
                "price": str(change['stopLossOnFill']['price'])
            }
        if "takeProfitOnFill" in change:
            new_payload["takeProfitOnFill"] = {
                "price": str(change['takeProfitOnFill']['price'])
            }

        # Iterate over child accounts to modify their corresponding orders
        for child_account in master_account.child_accounts.values():
            try:
                response = child_account.brokerage.modify_order(child_order_id, new_payload)
                print(f"Modified order {child_order_id} for child account {child_account.account_id}: {response}")
            except Exception as e:
                print(f"Error modifying order {child_order_id} for child account {child_account.account_id}: {e}")

    async def process_new_order(self, master_account, change):
        print("NEW ORDER WILL BE PLACED!")
        if len(master_account.child_accounts) == 0:
            print("No child accounts found.")
            return

        for child_account in master_account.child_accountss.values():
            response = child_account.brokerage.create_order(parent_order= change)
            if response and "orderCreateTransaction" in response:
                child_order_id = response["orderCreateTransaction"]["id"]
                master_order_id = change["id"]
                print(f"Mapping master pending order {master_order_id} to child order {child_order_id}")
                self.order_mappings[master_order_id] = child_order_id

    async def process_trade_order_update(self, master_account, order):
        """
        Handle updates to stop loss or take profit on an open trade.
        Uses the master trade ID to look up the corresponding child trade IDs.
        For STOP_LOSS orders, the provided price becomes the new stop loss,
        and for TAKE_PROFIT orders, the price becomes the new take profit.
        """
        master_trade_id = order.get("tradeOpenedID") or order.get("tradeID")
        if not master_trade_id:
            print("No trade ID found; cannot update trade orders.")
            return

        order_type = order.get("type", "").upper()
        if order_type == "STOP_LOSS":
            stop_loss = order.get("price")
            take_profit = None
        elif order_type == "TAKE_PROFIT":
            stop_loss = None
            take_profit = order.get("price")
        else:
            stop_loss = order.get("stopLossOnFill", {}).get("price")
            take_profit = order.get("takeProfitOnFill", {}).get("price")

        print(f"Updating trade {master_trade_id} with stop_loss: {stop_loss}, take_profit: {take_profit}")

        # For each child account, look up the corresponding child trade ID.
        for child_account in master_account.child_accounts.values():
            child_trade_id = self.trade_mappings.get(master_trade_id, {}).get(child_account.account_id)
            if not child_trade_id:
                print(f"No mapping for master trade {master_trade_id} on child account {child_account.account_id}, skipping update.")
                continue
            try:
                response = child_account.brokerage.update_trade_orders(child_trade_id, stop_loss, take_profit)
                print(f"Updated trade orders for trade {child_trade_id} on child account {child_account.account_id}: {response}")
            except Exception as e:
                print(f"Error updating trade orders on child account {child_account.account_id}: {e}")

    async def process_order_cancellations(self, master_account, change):
        print("ORDER CANCELLATIONS WILL BE PLACED!")
        if len(master_account.child_accounts) == 0:
            print("No child accounts found.")
            return

        order_id = change.get("orderID")
        if not order_id:
            print("No order ID found in the change; skipping cancellation.")
            return

        for child_account in master_account.child_accounts.values():
            pass

    @staticmethod
    def is_market_closeout(order):
        reason = order.get("reason", "")
        position_fill = order.get("positionFill", "")
        if reason == "POSITION_CLOSEOUT":
            return True
        if position_fill == "REDUCE_ONLY":
            return True
        return False

    async def process_market_order(self, master_account, order):
        master_order_id = order['id']
        if master_order_id in self.order_mappings:
            print(f"Market order fill {master_order_id} already processed; skipping replication.")
            return

        if self.is_market_closeout(order):
            await self.process_market_close(master_account, order)
        else:
            await self.process_market_open(master_account, order)

    async def process_market_open(self, master_account, order):
        print(f"(Line 285 in copier.py) MARKET ORDER OPEN WILL BE PLACED")
        master_order_id = order['id']
        master_trade_id = order.get("tradeOpenedID") or order.get("tradeID")

        for child_account in master_account.child_accounts.values():
            try:
                response = child_account.brokerage.create_order(parent_order= order)
                self.order_mappings[master_order_id] = response["orderCreateTransaction"]["id"]

                fill_transaction = response.get("fillTransaction")
                if fill_transaction and "tradeOpened" in fill_transaction:
                    child_trade_id = fill_transaction["tradeOpened"]["tradeID"]
                    if master_trade_id and child_trade_id:
                        self.trade_mappings.setdefault(master_trade_id, {})[child_account.account_id] = child_trade_id

            except Exception as e:
                print(f"Error placing market OPEN order on child account {child_account.account_id}: {e}")

    async def process_market_close(self, master_account, order):
        print(f"(Line 304 in copier.py) MARKET ORDER CLOSE WILL BE PLACED")
        master_trades_closed = order.get("tradesClosedIDs") or []
        if not master_trades_closed:
            fallback_trade = order.get("tradeID")
            if fallback_trade:
                master_trades_closed.append(fallback_trade)

        close_units = order.get("units")

        for master_trade_id in master_trades_closed:
            for child_account in master_account.child_accounts.values():
                child_trade_id = self.trade_mappings.get(master_trade_id, {}).get(child_account.account_id)
                if not child_trade_id:
                    print(f"(Line 317 in copier.py) No mapping for master trade {master_trade_id} on child account {child_account.account_id}, skipping close.")
                    continue

                child_close_units = None

                try:
                    response = child_account.brokerage.close_open_trade(child_trade_id, child_close_units)
                    print(f"(Line 324 in copier.py) Closed trade {child_trade_id} on child account {child_account.account_id}: {response}")
                    return
                except Exception as e:
                    print(f"(Line 327 in copier.py) Error closing trade {child_trade_id} on child account {child_account.account_id}: {e}")
                    raise


    # async def process_users(self):
    #     print("TRADE COPIER WORKING: Status:", self.status)
    #     while self.status == "active":
    #         # Get all users from AVL tree
    #         users = db.inorder_traversal()
    #         print('users:', users)
    #         # Process each user's master accounts
    #         for user in users:
    #             await self.process_user_accounts(user) 
    #         # Sleep until next poll
    #         await asyncio.sleep(self.poll_interval.total_seconds())
    #     print("TRADE COPIER STOPPED: Status:", self.status)

    # async def process_user_accounts(self, user):
    #     # Get master accounts
    #     master_accounts = user.get_master_accounts()
    #     print(f"MASTER ACCOUNTS: {master_accounts}")
    #     # For each master account:
    #     for master_account in master_accounts:
    #         # Get pending orders
    #         last_transaction_id = master_account.get_last_transaction_id()
    #         pending_orders = master_account.get_pending_orders()
    #         print(f"PENDING ORDERS: {pending_orders}")
    #     #     # Get child accounts
    #     #     child_accounts = user.get_child_accounts_by_master_account(master_account)
    #     #     # For each child account:
    #     #     for child_account in child_accounts:
    #     #         # Process orders
    #     #         self.process_orders(master_account, child_account, pending_orders)

    # async def process_order(self, master_account, child_account, order):
    #     pass
    #     # Check if order exists in mappings
    #     # If exists: Update order
    #     # If new: Create order

# Loop through all master accounts and get pending orders

# If the master account has pending orders, copy the orders to the child account

# If preexisting orders from the master account are modified, update the child account orders

# Check child account settings to see copying settings

# Place the orders on the child account

# Initialize and maintain state
# - Last known transaction IDs
# - Order mapping (master to child orders)
# - Account settings cache

# Monitor for closed/cancelled orders
# - Clean up order mappings
# - Handle partial closes
# - Update position tracking

# Handle error conditions
# - Network issues
# - API rate limits: 
# - Account restrictions
# - Insufficient margin

# Logging and monitoring
# - Trade copying activity
# - Error conditions
# - Performance metrics
# - Account status
