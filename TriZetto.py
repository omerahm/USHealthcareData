import requests

# API Endpoint
url = "https://api.trizetto.com/api/v1/insurance/providers/1336363258/patients/1CJ4J70FE79"

# Your access token (replace with your actual token)
access_token = "your_access_token"

# Set up the headers, including the authorization token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Make the API request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    insurance_details = response.json()
    print("Insurance Details:", insurance_details)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print("Error message:", response.text)
