# Solution Architecture
## UC10 - Enterprise Smart City Data Platform (ESCDP)

## 1. Architecture Overview
The platform integrates ten smart-city data domains through batch and event-based ingestion. PostgreSQL stores the ingested data and analytical warehouse, while Python and Pandas support data profiling and quality improvement.

## 2. Source Data Layer
The platform uses datasets representing:
1. Traffic
2. Public Transport
3. Parking
4. Water
5. Electricity
6. Waste Management
7. Environment and Air Quality
8. Emergency Services
9. Citizen Services
10. Property Tax

The source inventory will document the original source, download URL, file format, record count, and relevant fields for each dataset.

## 3. Batch Ingestion Layer
Technology: Pentaho Data Integration (Spoon)

Responsibilities:
- Read supported source files in their original formats.
- Configure input steps for CSV, JSON, XML, and other verified formats.
- Validate fields and data types.
- Route valid records to PostgreSQL staging tables.
- Capture rejected records and processing errors.
- Record ingestion timestamps and processing statistics.

## 4. Real-Time Demonstration Layer
Technology: Apache Kafka and Python

Components:
- Producer: publishes events to a Kafka topic.
- Kafka topic: transports events between producer and consumer.
- Consumer: reads events and writes them to a PostgreSQL staging table.
- Logging: records processed events and errors.

The event source must be documented. If historical records are replayed as events, the demonstration will be described as historical-data replay, not live sensor ingestion.

## 5. Staging Layer
Technology: PostgreSQL

Responsibilities:
- Store ingested records before analytical transformation.
- Preserve source identifiers and ingestion metadata where available.
- Support validation and reconciliation of source and loaded record counts.
- Separate staging tables by dataset or domain.

## 6. Data Quality and Transformation Layer
Technology: Python and Pandas, supported by SQL and Pentaho

Processing activities:
- Inspect column names and data types.
- Measure missing values and duplicate records.
- Identify invalid values and potential outliers.
- Standardize selected dates, categories, text fields, and numeric types.
- Document cleaning rules and rejected records.
- Generate profiling and data quality reports.

Original source files will be retained separately from cleaned outputs.

## 7. Data Warehouse Layer
Technology: PostgreSQL

The warehouse will use a dimensional model where appropriate:
- Dimension tables store descriptive entities and categories.
- Fact tables store measurable events or observations.
- Primary and foreign keys maintain relationships.
- Analytical SQL queries combine relevant domains where compatible keys and business definitions exist.

The exact fact tables, dimension tables, and grain will be finalized after examining the actual source schemas.

## 8. Reporting Layer
Technology: Power BI

Power BI will connect to the warehouse in the designated dashboard sprint to present relevant city indicators and trends.

## 9. End-to-End Data Flow

Batch path:
Source files -> Pentaho -> PostgreSQL staging -> Data quality and transformation -> PostgreSQL warehouse -> Power BI

Event path:
Documented event source -> Python producer -> Kafka topic -> Python consumer -> PostgreSQL staging

## 10. Operational Considerations
- Store database credentials outside source control.
- Log pipeline status, timestamps, record counts, and errors.
- Make ingestion repeatable and avoid unintended duplicate loading.
- Validate data before warehouse loading.
- Document data lineage from source to staging and warehouse.
- Verify source authenticity and record counts before accepting datasets.

## 11. Implementation Phases
Sprint 0: Requirements, project documentation, architecture, repository, and backlog.

Sprint 1: Source inventory, data dictionary, batch ingestion, staging tables, logging, and exception handling.

Sprint 2: Data profiling, data quality, standardization, dimensional modeling, warehouse loading, and analytical SQL.

Later sprint: Power BI dashboards and reporting.
