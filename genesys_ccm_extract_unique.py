import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

def load_files():
    print("Initializing file selection...")
    root = tk.Tk()
    root.withdraw()

    # Ask for CCM Excel file
    print("Please select the Genensys EMR PT Excel file.")
    ccm_path = filedialog.askopenfilename(title="Select Genensys EMR PT Excel File", filetypes=[("Excel Files", "*.xlsx")])
    if not ccm_path:
        print("No file selected. Exiting.")
        return None, None, None

    # Ask for CCIR CSV file
    print("Please select the CCIR CSV file.")
    ccir_path = filedialog.askopenfilename(title="Select CCIR CSV File", filetypes=[("CSV Files", "*.csv")])
    if not ccir_path:
        print("No CCIR file selected. Exiting.")
        return None, None, None

    # Ask for output Excel file path
    print("Please select the location to save the processed file.")
    output_path = filedialog.asksaveasfilename(title="Save Processed File As", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not output_path:
        print("No output path selected. Exiting.")
        return None, None, None

    print("Files selected successfully.")
    return ccm_path, ccir_path, output_path

def load_data(ccm_path, ccir_path):
    try:
        print("Loading CCM Excel file...")
        ccm_data = pd.read_excel(ccm_path)
        print("Loading CCIR CSV file...")
        ccir_data = pd.read_csv(ccir_path)
        print("Files loaded successfully.")
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
        print("Processing the data...")

        # Clean the 'icdCodes' column from CCM and split it into lists only if it is a string
        print("Splitting ICD codes...")
        ccm_data['icdCodes'] = ccm_data['icdCodes'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

        # Clean the CCIR data and filter by Chronic Indicator = 1
        print("Filtering CCIR data by Chronic Indicator...")
        ccir_data.columns = ['ICDCode', 'ICDDescription', 'ChronicIndicator']
        ccir_filtered = ccir_data[ccir_data['ChronicIndicator'] == '1'].copy()
        ccir_filtered['ICDCode'] = ccir_filtered['ICDCode'].str.strip("'")

        # Apply the matching function to the CCM data
        print("Matching ICD codes...")
        ccm_data['ICD Matched'] = ccm_data['icdCodes'].apply(lambda x: match_icd_codes(x, set(ccir_filtered['ICDCode']))[0])
        ccm_data['ICD Count'] = ccm_data['icdCodes'].apply(lambda x: match_icd_codes(x, set(ccir_filtered['ICDCode']))[1])

        # Convert relevant date columns to datetime, handling errors
        print("Converting date columns to datetime...")
        ccm_data['dateOfservice'] = pd.to_datetime(ccm_data['dateOfservice'], errors='coerce')

        # Remove rows with invalid dates
        invalid_dates = ccm_data['dateOfservice'].isnull().sum()
        if invalid_dates > 0:
            print(f"Removing {invalid_dates} rows with invalid dateOfservice values.")
        ccm_data = ccm_data.dropna(subset=['dateOfservice'])

        # Explicitly cast IDs to string after handling NaN values
        print("Converting IDs to strings...")
        ccm_data['claimId'] = ccm_data['claimId'].fillna('').astype(str)
        ccm_data['patientId'] = ccm_data['patientId'].fillna('').astype(str)
        ccm_data['primId'] = ccm_data['primId'].fillna('').astype(str)
        ccm_data['secId'] = ccm_data['secId'].fillna('').astype(str)

        # Filter rows where ICD count is 2 or more
        print("Filtering patients with ICD Count >= 2...")
        filtered_data = ccm_data[ccm_data['ICD Count'] >= 2]

        # Sort by patientId and dateOfservice to get the latest encounter
        print("Sorting data by latest encounter...")
        latest_encounters = filtered_data.sort_values(by=['patientId', 'dateOfservice'], ascending=[True, False])

        # Drop duplicates to keep only the latest encounter for each patient
        print("Dropping duplicate patients, keeping only latest encounters...")
        latest_encounters = latest_encounters.drop_duplicates(subset='patientId', keep='first')

        # Add a column for total encounters for each patient
        print("Adding total encounter count for each patient...")
        total_encounters = ccm_data.groupby('patientId').size().reset_index(name='total_encounters')

        # Merge the latest encounters with the total encounters data
        print("Merging the latest encounters with total encounter data...")
        latest_encounters_with_total = latest_encounters.merge(total_encounters, on='patientId', how='left')

        print("Data processing complete.")
        return latest_encounters_with_total

    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def save_data(filtered_data, output_path):
    try:
        print(f"Saving data to {output_path}...")
        filtered_data.to_excel(output_path, index=False)
        print(f"Filtered data saved to {output_path}")
    except Exception as e:
        print(f"Error saving the file: {e}")

def main():
    print("Starting process...")
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

    print("Process completed.")

if __name__ == "__main__":
    main()
