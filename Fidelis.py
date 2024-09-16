import requests
import socket

def test_dns_resolution(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"{hostname} resolved to {ip}")
    except socket.gaierror as e:
        print(f"Error resolving {hostname}: {e}")
        return False
    return True

def get_care_team(patient_id, api_key):
    hostname = "dev-int-api-gw.centene.com"
    url = f"https://{hostname}/fhir/v4/patientaccess/CareTeam"
    
    if not test_dns_resolution(hostname):
        print("DNS resolution failed. Check your network settings.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "patient": patient_id
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None

# Example usage
api_key = "your_api_key_here"  # Replace with your actual API key
patient_id = "12345"           # Replace with the actual patient ID

care_team_data = get_care_team(patient_id, api_key)
if care_team_data:
    print(care_team_data)
else:
    print("No data retrieved.")
