import requests
import base64

# Your WordPress site URL and credentials
site_url = "http://rahifs.local."
username = "admin"  # e.g., "admin"
app_password = "abcd-1234-efgh-5678"  # e.g., "abcd-1234-efgh-5678"

# Encode credentials for authentication
credentials = f"{username}:{app_password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers for API requests
headers = {
    "Authorization": f"Basic {encoded_credentials}"
}

# Test by fetching WooCommerce customers
customers_url = f"{site_url}/wp-json/wc/v3/customers"
response = requests.get(customers_url, headers=headers)

# Check the response
if response.status_code == 200:
    print("Success! Here’s the customer data:", response.json())
else:
    print("Error:", response.status_code, response.text)