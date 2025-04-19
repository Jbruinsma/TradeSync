from flask import Blueprint, redirect, url_for, session
from app import user_db


auth = Blueprint('auth', __name__)


@auth.route('/delete_account/<string:username>')
def delete_account(username):
    print("Deleting account")
    if user_db.contains(username):
        user_db.delete(username)
        return redirect(url_for('page.index'))
    else:
        return redirect(url_for('page.user_settings', username=username))
    
@auth.route('/remove_trade_account/<string:account_id>')
def remove_trade_account(account_id):
    try:
        username = session['username']
        user = user_db.search(username).val

        print(user.master_accounts)
        
        if account_id in user.master_accounts:
            del user.master_accounts[account_id]
            return redirect(url_for('page.accounts'))

        for master_id, master_account in user.master_accounts.items():
            if account_id in master_account.child_account_ids:
                del master_account.child_account_ids[account_id]
                del master_account.child_accounts[account_id]
                return redirect(url_for('page.accounts'))

        print(f"Account {account_id} not found")
        
    except Exception as e:
        print(f'Error removing trade account: {e}')
    return redirect(url_for('page.accounts'))
