import pandas as pd

grouped = pd.read_csv("grouped.csv") 
grouped_with_state = pd.read_csv("grouped_with_state.csv")

# --- Provider-level summary ---
provider_summary = grouped.groupby('Rndrng_NPI').agg(
    Total_Payments=('Avg_Mdcr_Pymt_Amt', 'sum'),
    Avg_Payment=('Avg_Mdcr_Pymt_Amt', 'mean'),
    Num_Tests=('HCPCS_Cd', 'nunique'),
    Outlier_Flag=('Outlier_Flag', 'max')
).reset_index()

provider_summary.to_csv("provider_summary.csv", index=False)

# --- Test-level summary ---
test_summary = grouped.groupby('HCPCS_Cd').agg(
    Num_Providers=('Rndrng_NPI', 'nunique'),
    Avg_Payment=('Avg_Mdcr_Pymt_Amt', 'mean'),
    Outlier_Providers=('Outlier_Flag', 'sum')
).reset_index()

test_summary.to_csv("test_summary.csv", index=False)

# --- State-level summary ---
state_summary = grouped_with_state.groupby('Rndrng_Prvdr_State_Abrvtn').agg(
    Total_Payments=('Avg_Mdcr_Pymt_Amt', 'sum'),
    Num_Providers=('Rndrng_NPI', 'nunique'),
    Outliers=('Outlier_Flag', 'sum')
).reset_index()

state_summary.to_csv("state_summary.csv", index=False)

print("provider_summary.csv, test_summary.csv, and state_summary.csv exported for Power BI.")



