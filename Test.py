import pandas as pd

# Create a simple DataFrame
df = pd.DataFrame({'Column1': [1, 2, 3], 'Column2': [4, 5, 6]})

# Save DataFrame to an Excel file
df.to_excel('test.xlsx', index=False)

# Read the Excel file
data = pd.read_excel('test.xlsx')
print(data)
