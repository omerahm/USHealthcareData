import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

def load_files():
    root = tk.Tk()
    root.withdraw()

    # Ask for CCM Excel file
    ccm_path = filedialog.askopenfilename(title="Select CCM Excel File", filetypes=[("Excel Files", "*.xlsx")])
    if not ccm_path:
        print("No CCM file selected. Exiting.")
        return None, None, None

    # Ask for CCIR CSV file
    ccir_path = filedialog.askopenfilename(title="Select CCIR CSV File", filetypes=[("CSV Files", "*.csv")])
    if not ccir_path:
        print("No CCIR file selected. Exiting.")
        return None, None, None

    # Ask for output Excel file path
    output_path = filedialog.asksaveasfilename(title="Save Filtered Report As", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not output_path:
        print("No output path selected. Exiting.")
        return None, None, None

    return ccm_path, ccir_path, output_path

def load_data(ccm_path, ccir_path):
    try:
        ccm_data = pd.read_excel(ccm_path)
        ccir_data = pd.read_csv(ccir_path)
        return ccm_data, ccir_data
    except Exception as e:
        print(f"Error loading files: {e}")
        return None, None

def match_icd_codes(icd_list, ccir_icd_codes):
    if isinstance(icd_list, list):
        matched_icds = [icd.strip() for icd in icd_list if icd.strip() in ccir_icd_codes]
        return matched_icds, len(matched_icds)
    return [], 0

def process_data(ccm_data, ccir_data):
    try:
        # Clean the 'icdCodes' column from CCM and split it into lists only if it is a string
        ccm_data['icdCodes'] = ccm_data['icdCodes'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

        # Clean the CCIR data and filter by Chronic Indicator = 1
        ccir_data.columns = ['ICDCode', 'ICDDescription', 'ChronicIndicator']
        ccir_filtered = ccir_data[ccir_data['ChronicIndicator'] == '1'].copy()
        ccir_filtered['ICDCode'] = ccir_filtered['ICDCode'].str.strip("'")

        # Apply the matching function to the CCM data
        ccm_data['ICD Matched'] = ccm_data['icdCodes'].apply(lambda x: match_icd_codes(x, set(ccir_filtered['ICDCode']))[0])
        ccm_data['ICD Count'] = ccm_data['icdCodes'].apply(lambda x: match_icd_codes(x, set(ccir_filtered['ICDCode']))[1])

        # Convert relevant date columns to datetime, handling errors
        ccm_data['dateOfservice'] = pd.to_datetime(ccm_data['dateOfservice'], errors='coerce')

        # Remove rows with invalid dates
        invalid_dates = ccm_data['dateOfservice'].isnull().sum()
        if invalid_dates > 0:
            print(f"Removing {invalid_dates} rows with invalid dateOfservice values.")
        ccm_data = ccm_data.dropna(subset=['dateOfservice'])

        # Ensure all other columns have consistent types using .loc[] and replace NaN values before converting to string
        ccm_data.loc[:, 'claimId'] = ccm_data['claimId'].fillna('').astype(str)
        ccm_data.loc[:, 'patientId'] = ccm_data['patientId'].fillna('').astype(str)
        ccm_data.loc[:, 'primId'] = ccm_data['primId'].fillna('').astype(str)
        ccm_data.loc[:, 'secId'] = ccm_data['secId'].fillna('').astype(str)

        # Group by relevant columns and aggregate data
        grouped_data = ccm_data.groupby(['claimId', 'patientId', 'patientName', 'dateOfBirth', 'dateOfservice', 
                                         'primaryInurance', 'primId', 'secondaryInsurance', 'secId', 'providername', 
                                         'serviceProvider', 'facility'], as_index=False).agg({
            'cptCode': lambda x: list(set(x)),
            'icdCodes': lambda x: list(set([item.strip() for sublist in x for item in sublist])),  # Flatten and deduplicate
            'ICD Matched': lambda x: list(set([item.strip() for sublist in x for item in sublist])),
            'ICD Count': 'max'
        })

        # Sort by date of service and filter by the latest date and ICD Count >= 2
        grouped_data_sorted = grouped_data.sort_values(by='dateOfservice', ascending=False)
        filtered_data = grouped_data_sorted.groupby(['claimId', 'patientId']).first().reset_index()
        filtered_data = filtered_data[filtered_data['ICD Count'] >= 2]

        return filtered_data
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def save_data(filtered_data, output_path):
    try:
        filtered_data.to_excel(output_path, index=False)
        print(f"Filtered data saved to {output_path}")
    except Exception as e:
        print(f"Error saving the file: {e}")

def main():
    ccm_path, ccir_path, output_path = load_files()

    if not ccm_path or not ccir_path or not output_path:
        return
    
    ccm_data, ccir_data = load_data(ccm_path, ccir_path)
    
    if ccm_data is None or ccir_data is None:
        print("Failed to load the data. Exiting.")
        return
    
    filtered_data = process_data(ccm_data, ccir_data)

    if filtered_data is not None:
        save_data(filtered_data, output_path)

if __name__ == "__main__":
    main()
