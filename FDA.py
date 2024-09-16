import requests

# Define the base URL for the OpenFDA drug endpoint
base_url = "https://api.fda.gov/drug/label.json"

# Define the parameters for the request
params = {
    "search": "active_ingredient:sodium",
    "limit": 1  # Limit the results to 1 for simplicity
}

# Make the request to the OpenFDA API
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Print the information about the drug
    if 'results' in data:
        for result in data['results']:
            print("Drug Name:", result.get('openfda', {}).get('brand_name', 'N/A'))
            print("Manufacturer:", result.get('openfda', {}).get('manufacturer_name', 'N/A'))
            print("Purpose:", result.get('purpose', 'N/A'))
            print("Warnings:", result.get('warnings', 'N/A'))
            print("Dosage and Administration:", result.get('dosage_and_administration', 'N/A'))
    else:
        print("No results found.")
else:
    print("Error:", response.status_code)
