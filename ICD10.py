import requests
import certifi

def get_access_token(client_id, client_secret):
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    payload = {
        'client_id': client_id, 
        'client_secret': client_secret, 
        'scope': 'icdapi_access', 
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_endpoint, data=payload, verify=certifi.where())
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception("Failed to obtain access token")

def get_icd10_info(icd_code, access_token):
    uri = f'https://id.who.int/icd/release/10/{icd_code.upper()}'  # Convert ICD code to uppercase
    headers = {
        'Authorization': f'Bearer {access_token}', 
        'Accept': 'application/json', 
        'Accept-Language': 'en', 
        'API-Version': 'v2'
    }
    response = requests.get(uri, headers=headers, verify=certifi.where())
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"ICD code {icd_code.upper()} not found or invalid request."}

def extract_years(release_urls):
    return [url.split('/')[-2] for url in release_urls]

# Main code
client_id = 'ba7fcdda-d06f-49ee-968d-97224adedc7b_353be121-94bd-4c69-9a37-c31593c6b4a3'
client_secret = 'RJvDhvEPxCDt5nGEEZbSOabz/OTjrNn04i2DdQf1HOw='

try:
    access_token = get_access_token(client_id, client_secret)
    icd_code = input("Enter the ICD code: ").strip().upper()  # Convert input to uppercase
    icd_info = get_icd10_info(icd_code, access_token)
    if "error" in icd_info:
        print(icd_info["error"])
    else:
        title = icd_info.get('title', {}).get('@value', 'No title available')
        latest_release_url = icd_info.get('latestRelease', '')
        latest_release_year = latest_release_url.split('/')[-2] if latest_release_url else 'No latest release available'
        all_release_urls = icd_info.get('release', [])
        all_release_years = extract_years(all_release_urls) if all_release_urls else ['No releases available']

        print(f"Title: {title}")
        print(f"Latest Release Year: {latest_release_year}")
        print(f"All Release Years: {', '.join(all_release_years)}")
except Exception as e:
    print(f"An error occurred: {e}")
