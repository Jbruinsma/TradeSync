from app import user_db
from app.models.master_account import MasterAccount


class ProfitManager:
    def __init__(self):
        self.status = "idle"

    def start(self):
        self.status = "active"

    def stop(self):
        self.status = "idle"

    @staticmethod
    def reset_daily_pl():
        # Reset daily profit/loss for all users
        users = user_db.inorder_traversal()
        for user in users:
            for account in user.master_accounts.values():
                for child_account in account.child_accounts.values():
                    child_account.profits['day'] = 0
                account.profits['day'] = 0