import requests

def search_icd10cm(term, max_list=7):
    base_url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
    params = {
        "sf": "code,name",
        "terms": term,
        "maxList": max_list
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

# Example usage
term = input("Enter the search term: ")
results = search_icd10cm(term)
print(results)
