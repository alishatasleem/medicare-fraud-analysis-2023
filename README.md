# Medicare Fraud Data Analysis (Pathology Subset, 2023)

## Overview
This project is an end-to-end healthcare data analysis of the **2023 CMS Medicare Physician & Other Supplier Public Use File (PUF)**, focused specifically on **pathology-related providers and procedures**.

The goal is to identify **unusual billing behavior** among pathology providers that may indicate potential fraud or anomalous billing patterns, using statistical outlier detection and an interactive **Power BI dashboard**.

---

## Data Source
- **Dataset:** Medicare Physician & Other Supplier Public Use File (PUF)
- **Year:** 2023
- **Publisher:** Centers for Medicare & Medicaid Services (CMS)
- **Source:** https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-geography-and-service/data

The dataset was filtered to include only providers classified under **Pathology**.

Raw CMS data is **not included** in this repository due to licensing and file size constraints.

---

## Methodology
The analysis was conducted at the **provider–procedure (HCPCS code)** level and uses two complementary statistical approaches:

- **Interquartile Range (IQR):** Detects providers whose average Medicare payments fall significantly outside the typical range for a given test.
- **Z-Score Analysis:** Identifies providers whose billing deviates substantially from the mean within each test group.

Providers may be flagged by:
- IQR only
- Z-score only
- Both methods (highest level of concern)

A combined outlier flag is used to summarize results.

---

## Repository Structure

```text
medicare-fraud-analysis-2023/
├── scripts/          # Python scripts for data processing and outlier detection
├── data/
│   ├── processed/    # Aggregated datasets used for analysis and visualization
│   └── sample/       # Placeholder for sample data (raw CMS data not included)
├── dashboard/        # Power BI dashboard file
├── docs/             # Documentation and dashboard screenshots
└── README.md

---

## How to Run
1. Clone this repository
2. Download the 2023 Medicare Physician & Other Supplier PUF from the CMS website (linked in Data Source)
3. Run the Python scripts in the `scripts/` directory to generate processed datasets.
4. Open the Power BI dashboard file in the `dashboard/` folder and connect it to the processed data outputs.

Raw CMS data is not included in this repository due to licensing restrictions.

---

## Dashboard
The Power BI dashboard provides:
- Key summary metrics (total payments, providers, flagged providers)
- Top pathology providers by total and average Medicare payments
- Geographic distribution of Medicare payments by state
- Distribution of average payments per provider
- Visual indicators showing which outlier detection method(s) flagged a provider

---

## Tools & Technologies
- **Python** (pandas, scipy) for data processing and statistical analysis
- **Power BI** for interactive visualization
- **Excel** for intermediate processed datasets

---

## Notes
- This project is for **analytical and educational purposes only**.
- Flagged providers represent **statistical anomalies**, not confirmed fraud.
- All analysis is based on publicly available CMS data.

---

## Author
Alisha Abdul Tasleem
