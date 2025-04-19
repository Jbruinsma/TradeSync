from flask import Blueprint, jsonify

from app import user_db
from app.models.brokerage.oanda_brokerage.oanda import OANDA

api = Blueprint('api', __name__)

@api.route('/account/<string:account_id>', methods=['GET'])
def account(account_id):
    """
        GET /account/<account_id>
        Retrieves a summary of a specific trade account by its unique account_id.

        Path Parameters:
        - account_id (string): The unique identifier of the account to retrieve.

        Returns:
        A JSON object containing:
        - customName (string): The user-defined name for the account.
        - brokerage (string): The name of the associated brokerage (e.g., "oanda").
        - accountID (string): The unique account identifier.
        - includeInPortfolio (bool): Whether the account is included in the portfolio.

        Example Response:
        {
            "customName": "My Live Account",
            "brokerage": "oanda",
            "accountID": "101-001-31017856-001",
            "includeInPortfolio": true
        }
    """
    trade_account = user_db.find_account(account_id)
    print(f"(Line 10 in api.py) ACCOUNT: {trade_account}")
    if isinstance(trade_account.brokerage, OANDA):
        brokerage = "oanda"
    else:
        brokerage = "NONE. ERROR."
    account_summary = {"customName": trade_account.custom_name,
                       "brokerage": brokerage,
                       "accountID": trade_account.account_id,
                       "includeInPortfolio": trade_account.include_in_portfolio}
    return jsonify(account_summary)