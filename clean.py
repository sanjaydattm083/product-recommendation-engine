import pandas as pd

# Load the raw data, same as before
df = pd.read_csv('data.csv', encoding='latin1')

print("Before cleaning:", df.shape)

# Step 1: Remove rows where Description is missing
# .notna() checks each row: True if there's a real value, False if blank
df = df[df['Description'].notna()]

# Step 2: Remove cancelled orders
# InvoiceNo is text (like '536365' or 'C536379'), so we check if it starts with 'C'
# The ~ symbol means "NOT" - so we keep rows that do NOT start with C
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]

print("After cleaning:", df.shape)

# Save the cleaned version to a new file, so we never touch the original data.csv
df.to_csv('clean_data.csv', index=False)
print("Saved as clean_data.csv")
