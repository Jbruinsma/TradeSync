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
        for master_account in user.master_accounts.values():
            if not master_account.active_copier:
                continue

            acct_id = master_account.account_id
            if acct_id not in self.last_transaction_ids:
                try:
                    self.last_transaction_ids[acct_id] = master_account.brokerage.get_current_transaction_id()
                except Exception as e:
                    print(f"Error fetching current transaction ID: {e}")
                    continue

            since = self.last_transaction_ids[acct_id]
            try:
                resp = master_account.brokerage.get_account_changes(since)
            except Exception as e:
                print(f"Error getting account changes: {e}")
                continue
            if not resp:
                continue

            changes = resp["changes"]
            self.last_transaction_ids[acct_id] = resp["last_transaction_id"]

            for child in master_account.child_accounts.values():
                await self.handle_account_changes(child.brokerage, changes)

    async def handle_account_changes(self, child: OANDA, changes: Dict):
        # 1) New orders (excluding pure SL/TP attachments)
        for order in changes.get("ordersCreated", []):
            if "replacesOrderID" not in order and order.get("type") not in ("TAKE_PROFIT", "STOP_LOSS"):
                await self.handle_new_order(child, order)

        # 2) Cancellations & modifications
        for order in changes.get("ordersCancelled", []):
            if "replacedByOrderID" in order:
                await self.handle_order_modification(child, order, changes)
            else:
                await self.handle_order_cancellation(child, order)

        # 3) Fills
        for order in changes.get("ordersFilled", []):
            await self.handle_order_fill(child, order)

        # 4) Trade closures
        for trade in changes.get("tradesClosed", []):
            await self.handle_trade_closure(child, trade)

        # 5) Batch SL/TP attachments
        per_trade: Dict[str, Dict[str, str]] = {}
        for o in changes.get("ordersCreated", []):
            if o.get("type") in ("TAKE_PROFIT", "STOP_LOSS") and "tradeID" in o:
                grp = per_trade.setdefault(o["tradeID"], {})
                grp[o["type"]] = o["price"]
        for m_tid, vals in per_trade.items():
            c_tid = self.trade_mappings.get(m_tid)
            if not c_tid:
                print(f"[TC] ⚠️ No child mapping for master trade {m_tid}")
                continue
            sl = vals.get("STOP_LOSS")
            tp = vals.get("TAKE_PROFIT")
            try:
                child.update_trade_orders(c_tid, stop_loss=sl, take_profit=tp)
            except Exception as e:
                print(f"[TC] Error updating SL/TP on {c_tid}: {e}")

    async def handle_new_order(self, child: OANDA, order: Dict):
        master_oid = order.get("id")
        try:
            resp = child.create_order(order)
            if not resp:
                return

            # map master order -> child order
            cot = resp.get("orderCreateTransaction")
            if cot:
                self.order_mappings[master_oid] = cot["id"]

            # if immediately filled
            ft = resp.get("orderFillTransaction")
            if ft and "tradeOpened" in ft:
                c_tid = ft["tradeOpened"]["tradeID"]
                # map by master order
                self.trade_mappings[master_oid] = c_tid
                # map by master trade ID if present
                m_tid = order.get("tradeOpenedID") or order.get("fillingTransactionID")
                if m_tid:
                    self.trade_mappings[str(m_tid)] = c_tid
        except Exception as e:
            print(f"Error creating child order for master {master_oid}: {e}")

    async def handle_order_modification(self, child: OANDA, old: Dict, changes: Dict):
        master_oid = old.get("id")
        new_oid = old.get("replacedByOrderID")
        if master_oid not in self.order_mappings:
            return
        try:
            # cancel using master ID
            child.cancel_order(master_oid)
            del self.order_mappings[master_oid]

            # re-create new
            new_order = next((o for o in changes.get("ordersCreated", []) if o.get("id") == new_oid), None)
            if new_order:
                await self.handle_new_order(child, new_order)
        except Exception as e:
            print(f"Error modifying child order for master {master_oid}: {e}")

    async def handle_order_fill(self, child: OANDA, order: Dict):
        if order.get("type") == "MARKET":
            await self.handle_new_order(child, order)
            return
        # for LIMIT/STOP fills, map master trade -> child trade
        m_oid = order.get("id")
        m_tid = order.get("tradeOpenedID") or order.get("tradeID")
        if not m_tid:
            return
        c_tid = self.trade_mappings.get(str(m_oid))
        if c_tid:
            self.trade_mappings[str(m_tid)] = c_tid

    async def handle_trade_closure(self, child: OANDA, trade: Dict):
        m_tid = trade.get("id")
        c_tid = self.trade_mappings.get(m_tid)
        if not c_tid:
            return
        # fetch child open trades
        try:
            open_resp = child.get_open_trades()
            open_ids = {t['id'] for t in open_resp.get('trades', [])}
        except Exception:
            open_ids = set()
        if c_tid in open_ids:
            try:
                child.close_open_trade(c_tid, None)
            except Exception as e:
                print(f"Error closing child trade {c_tid}: {e}")
        # cleanup
        del self.trade_mappings[m_tid]
        # also cleanup any related SL/TP mappings
        tp_oid = trade.get("takeProfitOrderID")
        sl_oid = trade.get("stopLossOrderID")
        if tp_oid in self.order_mappings:
            del self.order_mappings[tp_oid]
        if sl_oid in self.order_mappings:
            del self.order_mappings[sl_oid]

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

    async def handle_order_cancellation(self, child: OANDA, order: Dict):
        master_oid = order.get("id")
        if master_oid not in self.order_mappings:
            return
        try:
            child.cancel_order(master_oid)
        except Exception as e:
            print(f"Error cancelling child for master {master_oid}: {e}")
        finally:
            del self.order_mappings[master_oid]