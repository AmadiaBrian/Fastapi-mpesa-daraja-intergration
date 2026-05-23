import requests

def get_access_token(request=None):
    consumer_key = "opWeqfbSeWQg0lxBf1OWiUuFGzvOAxWm1mJQG2G46kpPVOMJ"  # Fill with your app Consumer Key
    consumer_secret = "6hU1YYlvAX6I9K5z9e9AS3RVH5D993lM5PL78pjcBevO9KeTlIUwFUchwKDR25Yi"  # Fill with your app Consumer Secret
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        print(f"Access token response status: {response.status_code}")
        print(f"Access token response text: {response.text}")
        response.raise_for_status()  # Raise exception for non-2xx status codes
        result = response.json()
        access_token = result['access_token']
        print(f"Access token generated successfully")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Error generating access token: {e}")
        print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
        print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
        return None
    