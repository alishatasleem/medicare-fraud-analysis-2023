import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

# Load preprocessed datasets
grouped = pd.read_csv("grouped.csv")            # provider–test level data (with outlier flags)
lab_data = pd.read_csv("lab_data_filtered.csv") # filtered raw lab data (with provider state info)

# -------------------------------------------------
# HISTOGRAMS: distribution of average Medicare payments
# -------------------------------------------------

# Load only the column we need for payments (lighter + faster)
df = pd.read_csv("grouped.csv", usecols=["Avg_Mdcr_Pymt_Amt"])

# Drop any missing values in that column (sanity check)
df = df.dropna(subset=["Avg_Mdcr_Pymt_Amt"])

# --- Histogram 1: full distribution ---
plt.figure(figsize=(10, 6))
plt.hist(df["Avg_Mdcr_Pymt_Amt"], bins=50)   # divide into 50 bins (bars)
plt.title("Histogram of Average Medicare Payments")
plt.xlabel("Avg Medicare Payment ($)")
plt.ylabel("Number of Provider–Test Pairs")
plt.tight_layout()
plt.show()

# --- Histogram 2: zoomed into <= 99th percentile ---
# Outliers can stretch the axis, hiding the "main body" of payments.
# So we zoom in to payments up to the 99th percentile.
q99 = df["Avg_Mdcr_Pymt_Amt"].quantile(0.99)
core = df[df["Avg_Mdcr_Pymt_Amt"] <= q99]

plt.figure(figsize=(10, 6))
plt.hist(core["Avg_Mdcr_Pymt_Amt"], bins=50)
plt.title("Histogram (zoomed to <= 99th percentile)")
plt.xlabel("Avg Medicare Payment ($)")
plt.ylabel("Number of Provider–Test Pairs")
plt.tight_layout()
plt.show()

# -------------------------------------------------
# BOXPLOT: compare distributions across top test codes
# -------------------------------------------------

# Pick top 20 most common test codes (by frequency)
top_tests = grouped['HCPCS_Cd'].value_counts().index[:20]

# Subset only those test codes for visualization
subset = grouped[grouped['HCPCS_Cd'].isin(top_tests)]

plt.figure(figsize=(14, 6))
sns.boxplot(data=subset, x='HCPCS_Cd', y='Avg_Mdcr_Pymt_Amt')

plt.xticks(rotation=45)  # rotate labels so they don’t overlap
plt.title("Boxplot of Average Medicare Payments by Test Code (Top 20)")
plt.xlabel("Test Code (HCPCS)")
plt.ylabel("Average Medicare Payment ($)")
plt.tight_layout()
plt.show()

# -------------------------------------------------
# SCATTERPLOT: highlight top 10 test codes
# -------------------------------------------------

# STEP 1: find top 10 test codes (by frequency of use)
top_tests = grouped['HCPCS_Cd'].value_counts().nlargest(10).index

# Label only those 10 tests, others marked as "Other"
grouped['Top_Test'] = grouped['HCPCS_Cd'].where(
    grouped['HCPCS_Cd'].isin(top_tests),
    other='Other'
)

# STEP 2: scatterplot of provider vs payment (only top 10 test codes shown)
plt.figure(figsize=(12, 6))
subset_top10 = grouped[grouped['HCPCS_Cd'].isin(top_tests)]
sns.scatterplot(
    data=subset_top10,
    x='Rndrng_NPI',              # provider ID
    y='Avg_Mdcr_Pymt_Amt',       # average payment
    hue='HCPCS_Cd',              # color = test code
    palette='tab10',
    alpha=0.6,                   # make points a bit transparent
    s=15                         # point size
)

plt.title("Scatterplot of Providers vs. Avg Medicare Payment (Top 10 Tests Highlighted)")
plt.xlabel("Provider ID (NPI)")
plt.ylabel("Average Medicare Payment ($)")
plt.legend(title="Test Code (HCPCS)", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# -------------------------------------------------
# BAR CHART: top 20 providers by total billing
# -------------------------------------------------

# STEP 1: total billing per provider
provider_totals = grouped.groupby('Rndrng_NPI')['Avg_Mdcr_Pymt_Amt'].sum().reset_index()

# STEP 2: sort providers by billing
provider_totals = provider_totals.sort_values(by='Avg_Mdcr_Pymt_Amt', ascending=False)

# STEP 3: take top 20
topn_providers = provider_totals.head(20)

# STEP 4: bar chart
plt.figure(figsize=(10,6))
bars = plt.bar(topn_providers['Rndrng_NPI'].astype(str), topn_providers['Avg_Mdcr_Pymt_Amt'])

plt.title("Top 20 Providers by Total Medicare Billing", fontsize=14)
plt.xlabel("Provider ID (NPI)", fontsize=12)
plt.ylabel("Total Medicare Payments ($)", fontsize=12)
plt.xticks(rotation=45, ha="right")

# Add numeric labels above bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:,.0f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()

# -------------------------------------------------
# HEATMAP: correlation between provider features
# -------------------------------------------------

# Summarize data at provider level
provider_summary = grouped.groupby('Rndrng_NPI').agg(
    Total_Payments=('Avg_Mdcr_Pymt_Amt', 'sum'),
    Avg_Payment=('Avg_Mdcr_Pymt_Amt', 'mean'),
    Num_Tests=('HCPCS_Cd', 'nunique'),
    Outlier_Flag=('Outlier_Flag', 'max')  # if any test flagged, mark provider as flagged
).reset_index()

# Compute correlation matrix
corr = provider_summary[['Total_Payments', 'Avg_Payment', 'Num_Tests', 'Outlier_Flag']].corr()

# Plot heatmap with seaborn
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap of Provider Features", fontsize=14)
plt.show()

# -------------------------------------------------
# CHOROPLETH MAPS: geographic patterns
# -------------------------------------------------

# STEP 1: map providers to states
provider_state = lab_data[['Rndrng_NPI', 'Rndrng_Prvdr_State_Abrvtn']].drop_duplicates()

# STEP 2: merge into grouped (so every row has state info too)
grouped_with_state = grouped.merge(provider_state, on='Rndrng_NPI', how='left')
grouped_with_state.to_csv("grouped_with_state.csv", index=False)

# STEP 3: aggregate metrics by state
state_totals = grouped_with_state.groupby('Rndrng_Prvdr_State_Abrvtn').agg(
    Total_Payments=('Avg_Mdcr_Pymt_Amt', 'sum'),
    Avg_Payment=('Avg_Mdcr_Pymt_Amt', 'mean'),
    Num_Tests=('HCPCS_Cd', 'count'),
    Num_Providers=('Rndrng_NPI', 'nunique'),
    Outliers=('Outlier_Flag', 'sum')
).reset_index()

# --- Map 1: total payments ---
fig1 = px.choropleth(
    state_totals,
    locations="Rndrng_Prvdr_State_Abrvtn",
    locationmode="USA-states",
    color="Total_Payments",
    hover_name="Rndrng_Prvdr_State_Abrvtn",
    hover_data=["Num_Providers", "Num_Tests", "Outliers"],
    scope="usa",
    color_continuous_scale="Blues",
    title="Total Medicare Payments by State"
)
fig1.show()

# --- Map 2: flagged outliers ---
fig2 = px.choropleth(
    state_totals,
    locations="Rndrng_Prvdr_State_Abrvtn",
    locationmode="USA-states",
    color="Outliers",
    hover_name="Rndrng_Prvdr_State_Abrvtn",
    hover_data=["Total_Payments", "Num_Providers", "Num_Tests"],
    scope="usa",
    color_continuous_scale="Reds",
    title="Flagged Outlier Providers by State"
)
fig2.show()
