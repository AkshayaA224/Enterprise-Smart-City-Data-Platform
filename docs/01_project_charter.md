# Sprint 0 - Project Charter

## Project Title
UC10 - Enterprise Smart City Data Platform (ESCDP)

## 1. Project Overview
The Enterprise Smart City Data Platform integrates data from ten smart-city domains into a centralized platform. It supports batch ingestion and a Kafka-based real-time ingestion demonstration, followed by data quality processing and analytical data storage.

## 2. Problem Statement
Smart-city data is distributed across multiple domains and file formats. Integrating these datasets into a consistent platform is necessary to support reliable analysis and data-driven decision-making.

## 3. Objectives
- Integrate data from ten smart-city domains.
- Implement batch ingestion using Pentaho Data Integration.
- Demonstrate real-time event ingestion using Apache Kafka.
- Store ingested data in PostgreSQL staging tables.
- Profile, clean, and standardize data using Python and Pandas.
- Build a dimensional data warehouse for analytical queries.
- Prepare the platform for Power BI dashboards in a later sprint.

## 4. Data Domains
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

## 5. Technology Stack
- PostgreSQL
- Pentaho Data Integration (Spoon)
- Python and Pandas
- Apache Kafka
- Git
- Power BI

## 6. Project Scope
### In Scope
- Source inventory and data dictionary
- Batch data ingestion
- Kafka-based real-time demonstration
- PostgreSQL staging and warehouse schemas
- Data profiling, cleaning, and standardization
- Data quality reports and analytical SQL queries

### Out of Scope for the Initial Sprints
- Production deployment of live city sensors
- A production-grade distributed streaming platform
- Final Power BI dashboards before the designated dashboard sprint

## 7. Assumptions and Constraints
- Each required dataset must be verified for source authenticity and record count.
- Each dataset must contain at least 1,000 records.
- Real-time ingestion must use a documented event source. Historical replay must not be described as live sensor data.
- Dataset schemas and data types may differ across sources.
- Local development uses the installed PostgreSQL and Pentaho tools.

## 8. Sprint Deliverables
### Sprint 0
Project charter, business requirements, solution architecture, Git repository, and product backlog.

### Sprint 1
Source inventory, data dictionary, Pentaho ingestion transformations, PostgreSQL staging tables, and ingestion logging and exception handling.

### Sprint 2
Python profiling and data quality reports, data standardization, star schema, warehouse load, and analytical SQL queries.

## 9. Success Criteria
- All ten datasets have documented sources, formats, and verified record counts.
- Batch ingestion pipelines load valid records into PostgreSQL staging tables.
- Invalid records and ingestion failures are logged.
- Data quality and profiling reports are generated.
- The warehouse supports the required analytical queries.
- The Kafka demonstration successfully processes documented events.
