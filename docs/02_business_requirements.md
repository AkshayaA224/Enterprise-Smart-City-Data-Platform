# Business Requirements Document (BRD)

## 1. Project Name
UC10 - Enterprise Smart City Data Platform (ESCDP)

## 2. Purpose
The purpose of this platform is to integrate data from ten smart-city domains, process it consistently, and store it in PostgreSQL for analysis.

## 3. Business Problem
Smart-city data is available in different files, formats, and domain-specific structures. Without a unified ingestion and data management process, it is difficult to maintain consistent, reliable data for analysis.

## 4. Business Objectives
- Consolidate data from ten smart-city domains.
- Support batch ingestion using Pentaho Data Integration.
- Demonstrate event-based ingestion using Apache Kafka.
- Improve data quality through profiling, validation, and standardization.
- Store integrated data in a dimensional data warehouse.
- Support operational and analytical SQL queries.

## 5. Stakeholders
| Stakeholder | Responsibility |
|---|---|
| Project team | Develop and test the platform |
| Project guide | Review requirements and deliverables |
| City administrators | Potential consumers of city-level insights |
| Data analysts | Analyze integrated datasets |
| Data providers | Supply the source datasets |

## 6. Functional Requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Maintain an inventory of ten datasets and their sources | High |
| FR-02 | Record dataset schemas, fields, and data types | High |
| FR-03 | Ingest batch files through Pentaho | High |
| FR-04 | Store raw ingested records in PostgreSQL staging tables | High |
| FR-05 | Log ingestion status, record counts, and failures | High |
| FR-06 | Profile datasets using Python and Pandas | High |
| FR-07 | Identify missing values, duplicates, and invalid records | High |
| FR-08 | Standardize selected fields and data types | High |
| FR-09 | Create dimensional fact and dimension tables | High |
| FR-10 | Load standardized data into the warehouse | High |
| FR-11 | Demonstrate event ingestion through Kafka | High |
| FR-12 | Provide analytical SQL queries across relevant domains | Medium |
| FR-13 | Prepare integrated data for Power BI reporting | Medium |

## 7. Non-Functional Requirements
- Reliability: ingestion failures must be recorded.
- Data integrity: source data must be validated before warehouse loading.
- Maintainability: scripts, SQL, and Pentaho transformations must be organized.
- Traceability: dataset sources and processing steps must be documented.
- Reproducibility: data processing should be repeatable.
- Security: credentials and sensitive configuration must not be committed to Git.
- Performance: ingestion should handle the selected datasets within the available development environment.

## 8. Data Requirements
- Ten smart-city domains must be represented.
- Every dataset must be verified to contain at least 1,000 records.
- Sources must be genuine real-world sources and documented.
- Original file formats must be preserved.
- Missing values, duplicate records, and data-type inconsistencies must be assessed.
- Any historical replay used in the Kafka demonstration must be identified as replay.

## 9. Acceptance Criteria
- All ten sources are documented and verified.
- Batch ingestion successfully loads the selected datasets into staging.
- Ingestion logs capture success, failure, and record counts.
- Profiling and data quality reports are generated.
- Cleaned data is loaded into the warehouse schema.
- Required analytical queries execute successfully.
- The Kafka demonstration processes events successfully.
- Project documentation and code are maintained in Git.

## 10. Dependencies and Constraints
- PostgreSQL and Pentaho must be configured.
- Python dependencies must be installed.
- Kafka must be configured for the real-time demonstration.
- Source formats and schemas may differ.
- Processing is limited by local storage, memory, and available compute resources.
