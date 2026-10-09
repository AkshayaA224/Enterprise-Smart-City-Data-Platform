# UC10 - Enterprise Smart City Data Platform

## Project Objective
Develop a data platform that integrates smart-city data from multiple domains using batch and real-time ingestion.

## Data Domains
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

## Technology Stack
- PostgreSQL: staging and data warehouse
- Pentaho Data Integration: batch ETL
- Python and Pandas: data profiling and quality
- Apache Kafka: real-time ingestion demonstration
- Git: version control
- Power BI: dashboards in a later sprint

## Project Scope
The platform will ingest, validate, standardize, and integrate data from the ten domains. It will support scheduled batch ingestion and a Kafka-based real-time demonstration.

## Important Note
Real-time ingestion will be demonstrated using an explicitly documented event source. Historical data replay will be identified as replay rather than live sensor data.
