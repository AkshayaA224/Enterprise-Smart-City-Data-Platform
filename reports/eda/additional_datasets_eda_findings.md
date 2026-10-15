# EDA Findings — Additional Datasets

## Purpose
This report consolidates exploratory data analysis (EDA) and data-quality findings for Citizen Services, Emergency, Property Tax, Transport, Waste, and Water.

The findings distinguish direct checks performed during analysis from existing validation evidence reviewed. Raw source files have not been modified. Unknown field definitions and units remain unverified.

## 1. Citizen Services

**Source:** `citizen_services.csv`

- Source size reported: 555,892 records and 20 columns.
- Status counts: Closed — 542,608 (97.61%); Open — 13,284 (2.39%).
- No missing requested timestamps or updated timestamps.
- Expected timestamps are missing in 337,688 records (60.75%).
- Closure timestamps are missing in 13,284 records (2.39%).
- All closed records have closure timestamps; all open records lack closure timestamps in the checks performed.
- No unparseable nonblank timestamps or timestamps before the requested time were identified.
- Existing ETL validation evidence reports 555,892 staging and warehouse records, 555,892 distinct warehouse record IDs, no duplicate warehouse record IDs, no missing staging records in the warehouse, and no invalid latitude or longitude values.

**Limitation:** An earlier discrepancy in the Spoon execution-log count remains unexplained. The existing validation evidence does not by itself establish that every ETL step has been independently reprocessed.

## 2. Emergency

**Source:** `emergency.xml`

- 11,750 XML records were parsed; no empty records were found.
- No unparseable creation dates or unparseable nonblank closure dates were identified.
- No closure date earlier than the creation date was identified.
- Latitude and longitude values passed numerical range checks where present.
- Missing closure dates: 3,108 (26.45%).
- Missing coordinate pairs: 1,625 (13.83%).
- Missing locations: 877 (7.46%).
- There are 449 distinct incident-type labels, with no blank incident-type labels found.

**Limitation:** Missing closure dates do not establish whether an incident is still open. Numerical coordinate validity does not prove geographic accuracy. Incident labels should be preserved unless a verified standardization rule is approved.

## 3. Property Tax

**Source:** `property_tax.csv`

- The initial CSV read reported 411,168 data rows and 139 columns.
- Investigation of the file tail found an appended JSON error response indicating an internal error (HTTP status 500).
- The file contains 411,163 valid-looking CSV records followed by five lines belonging to the appended error response. The raw file has not been edited.
- The initial CSV read reported 62 repeated `PARID` groups, containing 124 rows. These rows are not exact duplicates.
- Differences within the repeated identifier groups were observed in `CBNTAXCLASS`, `FINTAXCLASS`, `PERIOD`, and `EXTRACRDT`.
- Five apparent incomplete records from the initial CSV read correspond to the appended error block rather than ordinary property records.

**Limitations:** The meaning of repeated `PARID` records has not been confirmed. Do not automatically delete or deduplicate them. Treat the appended error response as source contamination and preserve the original file for traceability.

## 4. Transport

**Source:** `transport.csv`

- 9,343 records and five columns.
- Date range: 2001-01-01 to 2026-07-31.
- No missing values or exact duplicate rows were identified.
- No duplicate `service_date` + `day_type` combinations were found.
- All service dates parsed successfully.
- Numeric conversion succeeded for bus, rail boardings, and total rides after removing thousands separators.
- No negative values were found in those three measures.
- `total_rides` matched `bus + rail_boardings` in every record checked.
- Day-type codes: W — 6,526; U — 1,487; A — 1,330.

**Limitation:** The definitions of day-type codes and measurement units were not confirmed from the available source context.

## 5. Waste

**Source:** `waste.csv`

- 2,124 records and seven columns.
- Coverage: January 2015 through December 2017, spanning 36 months.
- Five boroughs and 59 distinct borough/community-district pairs were identified.
- Every month contains 59 records.
- No duplicate `MONTH` + `BOROUGH` + `COMMUNITYDISTRICT` keys were found.
- No missing values, exact duplicate rows, numeric conversion failures, or negative values were found in the checks performed.
- Each borough maps to exactly one `BOROUGH_ID`.

**Limitation:** Measurement units and definitions should be confirmed from the source documentation before interpreting quantities.

## 6. Water

**Source:** `water.csv`

- 3,109 records and 28 columns.
- No exact duplicate rows or duplicate `cnty_fips` identifiers were found.
- Each `state_abb` value maps to one state name in the dataset.
- Missing values occur in 18 columns. The largest missing-value rate is `prop_sw` at 3.02%.
- `tmax_40`, `tmax_diff`, `ppt_40`, and `ppt_diff` each have 34 missing records (1.09%).
- `wh` has six missing records; `Qmm` has two. Several other fields have one missing record each.
- The checked proportion-like fields (`prop_sw`, `gini`, `pcollege`, `prent`, `psfh`, `papt`) have values within the interval [0, 1].
- Negative values occur in `dw`, `pgrowth`, `tmax_diff`, `ppt_diff`, and `cook_pvi`.
- The largest observed `house_dens` value is 36,542.38, compared with a median of 20.935.

**Limitations:** Negative values and extreme observations are not confirmed errors. Field definitions, units, and calculation methods are needed before classifying them. Missing values should be documented rather than automatically imputed or removed.

## Overall conclusion

The checks documented here identified several completeness issues, unusual values, and source limitations. No raw records were intentionally removed or corrected as part of this analysis.

These findings support EDA documentation; they do not certify that every source record is correct or that every ETL and warehouse process has been independently revalidated.

Before committing, review this report alongside the dataset-specific EDA outputs and the existing profiling and data-quality reports.
