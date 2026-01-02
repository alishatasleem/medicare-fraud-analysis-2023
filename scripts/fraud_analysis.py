import pandas as pd
from scipy import stats

"""
# This helps confirm that Python can access and read the file before loading it with pandas (sanity check)

file_path = 'MUP_PHY_R25_P05_V20_D23_Prov_Svc.csv'  

# Use the 'with' keyword to open the file. 
# 'with' - context manager to ensure the file is properly closed after reading, even if an error occurs
# 'open(file_path, 'r')' opens the file in read mode ('r' stands for read)

with open(file_path, 'r') as f:
    #'f' is just a variable name representing the open file object, to interact with the contents of the file.
    for _ in range(5):
        # f.readline() reads one line from the file each time it's called.
        print(f.readline()) 
"""


file_path = 'MUP_PHY_R25_P05_V20_D23_Prov_Svc.csv' 

# Set the size of the data chunks you want to load (this is customizable based off RAM size)
chunk_size = 100000

# Create an empty list to hold all the filtered data relating to lab procedures 
# As each chunk is processed, chunks containing only lab procedures will be added 
lab_chunks = []

# Start reading the file in chunks using a loop
# pd.read_csv() normally reads the whole file — but with 'chunksize', it reads only part at a time
for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):

    # From each chunk, select only the rows where the 'Provider Type' is 'Independent Laboratory'
    # We use the inner chunk[...] to filter rows: inside the brackets, chunk['Provider Type'] == 'Independent Laboratory' returns a boolean Series (True/False for each row)
    # The outer chunk[...] uses that to select only rows where the condition is True
    filtered_chunk = chunk[chunk['Rndrng_Prvdr_Type'] == 'Pathology']

    # Add the chunk with filtered rows to our lab_chunks list
    lab_chunks.append(filtered_chunk)

# Combine all filtered chunks (each with only lab-related rows) into one final DataFrame
# pd.concat() merges multiple DataFrames in the lab_chunks list into one large DataFrame
# ignore_index=True resets the row numbers so they run from 0 to n (instead of keeping old chunk indexes that may repeat)
lab_data = pd.concat(lab_chunks, ignore_index=True)
lab_data.to_csv("lab_data_filtered.csv", index=False)

"""# Count duplicates of (Provider, Test)
duplicates = lab_data.duplicated(subset=['HCPCS_Cd', 'Rndrng_NPI'])
print(duplicates.sum())"""

#To prevent duplicates
grouped = lab_data.groupby(['HCPCS_Cd', 'Rndrng_NPI'])['Avg_Mdcr_Pymt_Amt'].mean().reset_index()

# Define a function to flag outliers using IQR
def detect_outliers_iqr(df):
    Q1 = df['Avg_Mdcr_Pymt_Amt'].quantile(0.25)
    Q3 = df['Avg_Mdcr_Pymt_Amt'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df['Avg_Mdcr_Pymt_Amt'] < lower) | (df['Avg_Mdcr_Pymt_Amt'] > upper)]

# Apply it for EACH TEST code separately
iq_outliers = grouped.groupby('HCPCS_Cd').apply(detect_outliers_iqr,include_groups=False).reset_index(drop=True)

# Show sample suspicious entries
print("Suspicious overcharges (by test):")
print(iq_outliers.head())

# Define a function to flag outliers using Z-score
def detect_outliers_zscore(df):
    # Skip if standard deviation is 0 (i.e. all values are the same)
    if df['Avg_Mdcr_Pymt_Amt'].std() == 0:
        return pd.DataFrame(columns=df.columns)
    
    # Get just the payment values
    values = df['Avg_Mdcr_Pymt_Amt'].values
    
    # Calculate the Z-scores for these values
    z_scores = stats.zscore(values)
    
    # Add the Z-scores as a new column (for inspection if needed)
    df['Z_Score'] = z_scores
    
    # Keep only rows with Z-scores greater than 3 or less than -3 (typical threshold)
    outliers = df[(z_scores > 3) | (z_scores < -3)]
    
    return outliers

# STEP 3: Apply the function per test code
zscore_outliers = grouped.groupby('HCPCS_Cd').apply(detect_outliers_zscore, include_groups = False).reset_index(drop=True)

# STEP 4: Show some results
print("Z-Score Based Outliers:")
print(zscore_outliers.head())

# -----------------------------------------------------------
# Export for Manual Checks 
# -----------------------------------------------------------
# At this stage, we already have:
# - grouped: clean dataset with (HCPCS code, provider ID) pairs and their average Medicare payment.
# - detect_outliers_iqr: function that finds IQR-based outliers within each test group.
# - detect_outliers_zscore: function that finds Z-score-based outliers within each test group.
#
# Goal of this block:
#   1. Re-run outlier detection while keeping the HCPCS code column attached.
#   2. Add "flags" back into the grouped dataset to mark which providers/tests are suspicious.
#   3. Save results into CSVs for human auditors to open in Excel.
# -----------------------------------------------------------


# --- STEP 1: Run IQR outlier detection per HCPCS code ---
# groupby('HCPCS_Cd') -> split the dataset by test code.
# For each test group (g), run detect_outliers_iqr(g).
# .assign(HCPCS_Cd=g.name) -> reattach the HCPCS code to the outlier rows.
# reset_index(drop=True) -> reset row numbers for a clean dataframe.
iq_outliers = grouped.groupby('HCPCS_Cd').apply(
    lambda g: detect_outliers_iqr(g).assign(HCPCS_Cd=g.name)
).reset_index(drop=True)

# Preview the first 5 IQR-based suspicious rows
print(iq_outliers.head())


# --- STEP 2: Run Z-score outlier detection per HCPCS code ---
# Same logic as above, but using the Z-score method.
# This finds providers/tests that are statistically unusual even when the data distribution is tight.
zscore_outliers = grouped.groupby('HCPCS_Cd').apply(
    lambda g: detect_outliers_zscore(g).assign(HCPCS_Cd=g.name)
).reset_index(drop=True)

# Preview the first 5 Z-score-based suspicious rows
print(zscore_outliers.head())


# --- STEP 3: Add IQR flags back into the main dataset ---
# iq_outliers[['HCPCS_Cd', 'Rndrng_NPI']] -> select just test+provider IDs for suspicious rows.
# drop_duplicates() -> avoid duplicates in case the same provider/test was flagged multiple times.
# assign(IQR_Flag=1) -> add a column marking them as flagged (1).
# merge(..., how='left') -> join this flag info back into the grouped dataset.
grouped = grouped.merge(
    iq_outliers[['HCPCS_Cd', 'Rndrng_NPI']].drop_duplicates().assign(IQR_Flag=1),
    on=['HCPCS_Cd', 'Rndrng_NPI'],
    how='left'
)

# Any rows not in iq_outliers will have NaN in IQR_Flag, so we replace with 0.
grouped['IQR_Flag'] = grouped['IQR_Flag'].fillna(0).astype(int)
print("IQR_Flag column added. Number of rows flagged:", grouped['IQR_Flag'].sum())


# --- STEP 4: Add Z-score flags back into the main dataset ---
# Same process as IQR, but for Z-score outliers.
grouped = grouped.merge(
    zscore_outliers[['HCPCS_Cd', 'Rndrng_NPI']].drop_duplicates().assign(ZScore_Flag=1),
    on=['HCPCS_Cd', 'Rndrng_NPI'],
    how='left'
)

# Replace NaN with 0 for clean flag values.
grouped['ZScore_Flag'] = grouped['ZScore_Flag'].fillna(0).astype(int)
print("ZScore_Flag column added. Number of rows flagged:", grouped['ZScore_Flag'].sum())


# --- STEP 5: Create a combined master flag ---
# If a provider/test was flagged by either IQR or Z-score, mark as suspicious (1).
# If flagged by neither, mark as normal (0).
grouped['Outlier_Flag'] = grouped[['IQR_Flag', 'ZScore_Flag']].max(axis=1)
print("\nCreating combined Outlier_Flag column...")
print("Combined Outlier_Flag column added. Total flagged:", grouped['Outlier_Flag'].sum())


# --- STEP 6: Save results to CSVs ---
# Save the ENTIRE grouped dataset, with flags included.
# This is useful because auditors may want to see both suspicious and normal rows side by side.
print("\nSaving full grouped dataset to grouped.csv")
grouped.to_csv("grouped.csv", index=False)

# Save only suspicious rows where Outlier_Flag == 1.
# This makes it easier for investigators to focus only on potential fraud cases.
outliers_combined = grouped[grouped['Outlier_Flag'] == 1]
print("Suspicious outliers dataframe shape:", outliers_combined.shape)
print("Saving suspicious outliers to outliers.csv")
outliers_combined.to_csv("outliers.csv", index=False)


# --- STEP 7: Confirmation message ---
# Provide a friendly summary so you know the script worked as intended.
print("\nExport complete: 'grouped.csv' and 'outliers.csv' created.")
print("Total grouped rows:", grouped.shape[0])
print("Total flagged rows:", outliers_combined.shape[0])







