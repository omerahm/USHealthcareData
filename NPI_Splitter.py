import pandas as pd
import os

def split_csv_to_xlsx(input_csv_path, output_dir, rows_per_file=1048576):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV file in chunks
    chunk_iter = pd.read_csv(input_csv_path, chunksize=rows_per_file)

    for i, chunk in enumerate(chunk_iter):
        # Define output file path
        output_file_path = os.path.join(output_dir, f'output_chunk_{i + 1}.xlsx')

        # Save chunk to Excel file
        chunk.to_excel(output_file_path, index=False, engine='openpyxl')
        print(f'Saved {output_file_path}')

if __name__ == "__main__":
    input_csv_path = 'C:/Users/omera/npidata_pfile_20050523-20240707.csv'  # Update this path to your CSV file
    output_dir = 'C:/Users/omera/NPIData/'         # Update this path to your desired output directory

    split_csv_to_xlsx(input_csv_path, output_dir)