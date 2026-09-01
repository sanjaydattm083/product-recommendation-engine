import pandas as pd

# Load the CSV file into a table-like structure called a "DataFrame"
# encoding='latin1' is needed because this file has special characters
# (like £ signs) that Python's default reader can't handle
df = pd.read_csv('data.csv', encoding='latin1')

# Print the shape: (number of rows, number of columns)
print("Shape:", df.shape)

# Print the first 5 rows so we can see what the data looks like
print(df.head())

# Check how many values are missing in each column
print("\nMissing values:\n", df.isnull().sum())
