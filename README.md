# Part_D_RX_ETL
## Background
Processing data from CMS, Medicaid and Q1 LLC to create estimates of whether a single prescription would put an insured at risk of falling into the "donut hole" of Part D of Medicare.

Coded in Python using Jupyter Notebook using CSV's and MySql for storage.

---
## Extraction

Out-of-pocket co-payments for Medicare Part D recipients do not follow a particularly simple formula.  There are 4 possible basic cost shares that depend on the total cost of the prescriptions purchased through the program for the calendar year.  One of the most alarming cost shares occurs in the coverage gap, also known as the “donut hole”, where the cost of the drug falls mostly on the insured with little or possibly no coverage from the insurer.  On the other hand, despite being called catastrophic coverage, the cost share during that period is minimal and the burden falls mostly on the insurer.  For a patient who is on a single prescription throughout the year, would this patient end the year in the ”donut hole” or reach catastrophic coverage?

Another potential point of interest is actual acquisition costs of drugs (i.e. are providers upcharging for certain drugs more than others).  Considering potential markups for cheaper vs. more expensive drugs could be an item of interest.  

The first dataset contains aggregate costs (i.e. insurance and copayments) paid for prescription drugs used by Medicare Part D recipients in the year 2016.  It also contains some information about drugs, such as whether the drug is an opioid or an antibiotic.  This was available in csv format from Kaggle at https://www.kaggle.com/cms/cms-part-d-prescriber-summary-reports-2013-2016#part-d-prescriber-national-summary-report-calendar-year-2016.csv.  The data was sourced from the Center for Medicare and Medicaid Services.

The second dataset was the National Average Drug Acquisition Cost CSV from Medicaid.gov, the website for the Center for Medicaid and Children’s Health Insurance Program (CHIP).  This dataset has updates on the average unit cost for pharmacies to obtain the drug.  The data can be exported from https://data.medicaid.gov/Drug-Pricing-and-Payment/NADAC-National-Average-Drug-Acquisition-Cost-/a4y5-998d/data. 

Information on the Medicare Part-D coverage cut-offs for various years from Q1 Group LLC (https://q1medicare.com/PartD-The-MedicarePartDOutlookAllYears.php), a non-government group that gives information about Medicare.

---

## Transformation

### CMS Prescriber Summary (Aggregate Cost)
Columns were renamed and fixed for unnecessary spaces on the end of column labels.  Flags with NaN values (GH65 tag) were dropped and the others were converted from strings to booleans.  Average yearly cost per drug was derived from the total spend and number of claims per drug.  The number of claims were based on 30 day fills, so after finding the average cost for a 30-day fill, the annual was estimated to be 12 times that amount.

### NADAC
The column names seemed to be formatted appropriately, but some were dropped due to lack of relevance.  

The dataset was very inconsistent with its naming practice; the same drug could be abbreviated in different ways.  For example, hydrochlorothiazide might be spelled out, abbreviated as "hcl" or abbreviated as "hct" or "hctz" for various entries.  Although the chemical abbreviation is recognized as "hct"/"hctz", the common usage in prescriptions is "hcl".  Another complication was that many of the names have dosages that are not indicated in the CMS dataset.  The name was split by separating out any numbers, special characters, or keywords (ie. “tablet”) into separate columns.

Many of the rows were repeats of the same drug as there were updated measures throughout the year.  To cut down on entries the date was reformatted to be sort-friendly.  Then duplicates were dropped keeping only the entry with the most recent date.

The resulting simplification of the dataset is saved as a csv file for alternative manipulation.

### Q1 - Part D Coverage Table
The scrape of the html gave us a series of tables easily importable into a dataframe.  The resulting dataframe was sliced into 5 separate tables.

#### Combining the Tables
The extracted information from the Q1 data source was used to create bins to label the CMS dataset.  The 2016 threshold was used as most of the datasets are based on 2016.  2019 was also used to estimate the potential risk for next year based on the older numbers, but it's possible that the costs have gone down since 2016.  Assuming that the patient is paying for the prescription for the course of the calendar year, this process identifies the risk that the single drug would place a beneficiary into a particular cost sharing period in 2016/2019.

#### Index for Cross Reference
It was impractical to join the Prescriber Summary and NADAC tables as there was not a convenient common key to join on.  The most logical choice was to attempt to join on the drug name.  However, even after parsing the drug names for dosage to try to improve the matches, only about half of the NADAC table was able to find a match in the Prescriber Summary table.

In the interest of presenting as much data as possible, the two tables were kept separate.  After separating names from dosages in each table, a key of the best match based on the other table’s index was added (note that -1 indicates no match).

#### Column Names
The column names were formatted to convert spaces to underscores and make everything lower case.

---
## Loading
The data is set to be loaded into a MySQL database.  Five dataframes on different benefits and beneficiaries was loaded from the Coverage table along with the transformed Prescriber Summary and simplified NADAC tables for a total of 7. It does require that one run “CREATE DATABASE partD_rx_db;” prior to running the python code.  In order to set up the connection the user should also create a “keys.py” file which assigns values to the “mysql” as the address to the desired server to store the data, “user” as the user name and “pw” as password.

---
## Last Thoughts / TLDR;
The resulting tables should allow a user to estimate the risk of a particular prescription of putting one into a cost share portion of Medicare Part D based on the drug name as well as allow them to see what are the average pharmacy acquisition costs while bouncing between the two on the cross index keys.  It is still limited by inconsistent naming practices or the lack of data on drugs on which claims were not actually filed in 2016 depsite aquisition costs of those drugs changing (possibly the impact of low demand). 
