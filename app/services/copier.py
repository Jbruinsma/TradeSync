import asyncio

from app import user_db


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
        pass

    async def iterate_master_accounts(self):
        # Iterates through the MasterAccount Objects stored in the User object to check if a change has been made (Trade
        # Placed, Canceled, modified, etc.). MasterAccounts are stored in a dictionary.
        pass

    async def handle_child_accounts(self):
        # If a change has been detected, the change is reflected in the child accounts by iterating through the ChildAccounts in the MasterAccount object.
        pass