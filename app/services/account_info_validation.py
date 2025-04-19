import requests

def validate_oanda_credentials(api_key: str, account_id: str, is_live: bool) -> bool:
    """
    Simple validation of OANDA credentials by attempting to access the account summary
    """
    # Select the appropriate URL based on account type
    base_url = "https://api-fxtrade.oanda.com" if is_live else "https://api-fxpractice.oanda.com"
    
    # Set up the headers with the raw API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Attempt to get account summary
        endpoint = f"/v3/accounts/{account_id}/summary"
        response = requests.get(
            f"{base_url}{endpoint}",
            headers=headers
        )
        
        # Return True only if we get a successful response
        return response.status_code == 200
        
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False