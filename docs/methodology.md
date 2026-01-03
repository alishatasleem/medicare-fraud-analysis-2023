## Methodology

This project identifies **statistical anomalies in Medicare billing patterns** among pathology providers using Python-based data processing, statistical analysis, and visualization, followed by interactive dashboarding in Power BI.

The analytical workflow consists of the following steps:

1. **Data Ingestion**
   - The 2023 CMS Medicare Physician & Other Supplier Public Use File (PUF) was loaded into Python using pandas.

2. **Filtering and Preprocessing (Python)**
   - Data was programmatically filtered to include only pathology-related providers and procedures.
   - Analysis was conducted at the **provider–procedure (HCPCS code)** level.
   - Provider-level average Medicare payment amounts were computed.
   - State-level aggregations were generated to support geographic analysis.

3. **Exploratory Analysis and Visualization (Python)**
   - Summary statistics and visualizations were created in Python to inspect payment distributions and identify potential anomalies.
   - These visual checks informed threshold selection and outlier interpretation.

4. **Outlier Detection (Python)**
   Two complementary statistical methods were applied:
   - **Interquartile Range (IQR):** Flags providers whose average payments fall outside 1.5×IQR for a given HCPCS code.
   - **Z-score analysis:** Identifies providers whose average payments deviate significantly from the mean within each procedure group.

5. **Combined Flagging**
   - Providers may be flagged by IQR only, Z-score only, or both methods.
   - A combined outlier flag highlights providers with the strongest statistical deviations.

6. **Data Export and Interactive Visualization**
   - Processed datasets were exported from Python.
   - A Power BI dashboard was built to support interactive exploration by HCPCS code and geographic region.
