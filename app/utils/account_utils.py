def get_accounts_sum(user):
    if not user.master_accounts:
        return 0
    return len(user.master_accounts) + sum( len(account.child_accounts) for account in user.master_accounts.values())

def get_accounts_list(user):
    accounts = []
    for master_account in user.master_accounts.values():
        accounts.append(master_account)
        for child_account in master_account.child_accounts.values():
            accounts.append(child_account)
    return accounts

def get_master_accounts_list(user):
    master_accounts = []
    for master_account in user.master_accounts.values():
        master_accounts.append(master_account)
    return master_accounts

def get_child_accounts_list(user):
    child_accounts = []
    for master_account in user.master_accounts.values():
        for child_account in master_account.child_accounts.values():
            child_accounts.append(child_account)
    return child_accounts

def format_value(balance):
        if balance is not None:
            try:
                balance_float = float(balance)
                return "${:,}".format(balance_float)
            except (ValueError, TypeError):
                return "---"
        else:
            return "---"
        
def format_growth(balance, growth):
    return round((float(growth) / float(balance)) * 100, 2)
        
def get_total_open_positions(user):
    total_open_positions = 0
    for account in get_accounts_list(user):
        total_open_positions += account.get_open_positions()
    return total_open_positions
