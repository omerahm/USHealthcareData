import pandas as pd
import requests

# Set file paths (update these paths as per your local environment)
input_file_path = 'D:/NPI.xlsx'
output_file_path = 'D:/NPI_Output.xlsx'

# Load the Excel file
data = pd.read_excel(input_file_path, sheet_name='Sheet1')

# Normalize column names
data.columns = data.columns.str.strip().str.lower()

# Ensure the 'npi' column exists
if 'npi' not in data.columns:
    raise ValueError("The file does not contain an 'npi' column.")

# Function to fetch data from NPI Registry
def fetch_npi_details(npi_number):
    url = f'https://npiregistry.cms.hhs.gov/api/?number={npi_number}&version=2.1'
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json().get('results', [])
        if result:
            return result[0]
    return {}

# Fetch details for each NPI number and store in a list
npi_details_list = []
for npi in data['npi']:
    details = fetch_npi_details(npi)
    npi_details_list.append(details)

# Function to extract basic details
def extract_basic_details(npi_data):
    basic_info = npi_data.get('basic', {})
    authorized_official = {
        'first_name': basic_info.get('authorized_official_first_name', basic_info.get('first_name', '')),
        'last_name': basic_info.get('authorized_official_last_name', basic_info.get('last_name', '')),
        'middle_name': basic_info.get('authorized_official_middle_name', ''),
        'credential': basic_info.get('authorized_official_credential', basic_info.get('credential', '')),
        'gender': basic_info.get('authorized_official_gender', basic_info.get('gender', '')),
        'name_prefix': basic_info.get('authorized_official_name_prefix', basic_info.get('name_prefix', '')),
        'name_suffix': basic_info.get('authorized_official_name_suffix', basic_info.get('name_suffix', '')),
        'sole_proprietor': basic_info.get('sole_proprietor', basic_info.get('organizational_subpart', '')),
        'telephone_number': basic_info.get('authorized_official_telephone_number', ''),
        'title_or_position': basic_info.get('authorized_official_title_or_position', '')
    }
    return {
        'NPI': npi_data.get('number', ''),
        'Organization Name': basic_info.get('organization_name', ''),
        'First Name': authorized_official['first_name'],
        'Last Name': authorized_official['last_name'],
        'Middle Name': authorized_official['middle_name'],
        'Credential': authorized_official['credential'],
        'Sole Proprietor': authorized_official['sole_proprietor'],
        'Gender': authorized_official['gender'],
        'Enumeration Date': basic_info.get('enumeration_date', ''),
        'Last Updated': basic_info.get('last_updated', ''),
        'Certification Date': basic_info.get('certification_date', ''),
        'Status': basic_info.get('status', ''),
        'Name Prefix': authorized_official['name_prefix'],
        'Name Suffix': authorized_official['name_suffix'],
        'Telephone Number': authorized_official['telephone_number'],
        'Title or Position': authorized_official['title_or_position']
    }

# Function to extract address details
def extract_address_details(npi_data):
    addresses = npi_data.get('addresses', [])
    mailing_address = primary_address = secondary_address = {
        'address_1': '', 'address_2': '', 'city': '', 'state': '', 'postal_code': '', 'telephone_number': '', 'fax_number': ''}
    for address in addresses:
        if address.get('address_purpose') == 'MAILING':
            mailing_address = address
        elif address.get('address_purpose') == 'LOCATION':
            primary_address = address
        elif address.get('address_purpose') == 'SECONDARY':
            secondary_address = address
    return mailing_address, primary_address, secondary_address

# Function to extract taxonomy details
def extract_taxonomies(npi_data):
    taxonomies = npi_data.get('taxonomies', [])
    return ', '.join([taxonomy.get('desc', '') for taxonomy in taxonomies])

# Function to extract identifier details
def extract_identifiers(npi_data):
    identifiers = npi_data.get('identifiers', [])
    return ', '.join([identifier.get('identifier', '') for identifier in identifiers])

# Creating columns for each extracted detail
basic_info_list = []
mailing_address_list = []
primary_address_list = []
secondary_address_list = []
taxonomy_list = []
identifier_list = []

for npi in npi_details_list:
    basic_info = extract_basic_details(npi)
    mailing_address, primary_address, secondary_address = extract_address_details(npi)
    taxonomies = extract_taxonomies(npi)
    identifiers = extract_identifiers(npi)

    basic_info_list.append(basic_info)
    mailing_address_list.append(mailing_address)
    primary_address_list.append(primary_address)
    secondary_address_list.append(secondary_address)
    taxonomy_list.append(taxonomies)
    identifier_list.append(identifiers)

# Create DataFrames for each set of extracted details
basic_df = pd.DataFrame(basic_info_list)
mailing_address_df = pd.json_normalize(mailing_address_list)
primary_address_df = pd.json_normalize(primary_address_list)
secondary_address_df = pd.json_normalize(secondary_address_list)
taxonomy_df = pd.DataFrame(taxonomy_list, columns=['Taxonomies'])
identifier_df = pd.DataFrame(identifier_list, columns=['Identifiers'])

# Renaming address columns to include their type
mailing_address_df = mailing_address_df.add_prefix('Mailing ')
primary_address_df = primary_address_df.add_prefix('Primary ')
secondary_address_df = secondary_address_df.add_prefix('Secondary ')

# Concatenate all data
full_df = pd.concat([basic_df, mailing_address_df, primary_address_df, secondary_address_df, taxonomy_df, identifier_df], axis=1)

# Save the DataFrame to a new Excel file
with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
    data.to_excel(writer, sheet_name='Original Data', index=False)
    full_df.to_excel(writer, sheet_name='NPI Details', index=False)

print(f"Data has been successfully written to {output_file_path}")
