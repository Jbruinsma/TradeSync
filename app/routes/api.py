from flask import Blueprint, jsonify, request

from app import user_db
from app.models.brokerage.oanda_brokerage.oanda import OANDA

api = Blueprint('api', __name__)

# USER LEVEL ROUTES

@api.route('/users/<string:username>', methods=['GET'])
def accounts(username):
    """
    Returns a summary of the user's account information.
    """
    user_account = user_db.search(username)
    if not user_account:
        return jsonify({"error": "No accounts found for this user"}), 404
    else:
        user_account = user_account.val
    return jsonify(user_account.format_user_account_summary()), 200

# TRADE ACCOUNT LEVEL ROUTES

@api.route('/users/<username>/trade_accounts', methods=['GET'])
def trade_accounts(username):
    """
    Returns a dict of all trade account ids connected to the user.
    """
    user_account = user_db.search(username)
    if not user_account:
        return jsonify({"error": "No accounts found for this user"}), 404
    else:
        user_account = user_account.val
    return jsonify(user_account.format_user_trade_accounts()), 200

@api.route('/users/<string:username>/trade_accounts/<string:account_id>', methods=['GET'])
def account(username, account_id):
    """
    Returns a summary of the trade account information.
    """
    user_account = user_db.search(username)
    if not user_account:
        return jsonify({"error": "No accounts found for this user"}), 404
    else:
        user_account = user_account.val

    trade_account = user_account.get_account(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(trade_account.get_account_summary()), 200

# CHILD ACCOUNT ENDPOINTS

# ANALYTICS ENDPOINTS