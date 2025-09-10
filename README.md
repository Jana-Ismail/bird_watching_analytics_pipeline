# Bird Sightings + Weather Data Pipeline

This project is a data engineering pipeline that collects and integrates **bird observation data** with **weather data** to support analysis of how weather conditions affect bird activity and migration in California.

---

## Overview

The pipeline ingests raw data from multiple APIs (e.g., eBird, iNaturalist, NASA FIRMS, Weatherbit, Open-Meteo) and stores them in a structured format. Weather data and bird sightings are later joined on date and location for analysis.

The end goal is to enable research questions such as:
- How do weather conditions influence bird migration patterns?
- Are certain weather events correlated with higher or lower sighting frequencies?
- What seasonal or regional patterns emerge when combining bird and weather datasets?
- Can recent weather patterns be used to predict likeliness of bird sightings for bird watching enthusiasts?

---

## Features

- **API Ingestion**:  
  - Bird sightings from eBird and iNaturalist.  
  - Weather data from Open-Meteo(temperature, wind, precipitation), NASA FIRMS (fire/weather), and other sources.  

- **Data Storage**:  
  - Raw ingestion to MinIO object storage.  
  - Conversion from JSON to Parquet for efficient querying.  

- **Data Modeling**:  
  - Bronze → Silver → Gold transformations using DuckDB.  
  - Timezone alignment (UTC vs. Pacific) for consistent joins.
  - Coordinate mapping for regional determination   

- **Orchestration**:  
  - Scripts are modular and designed for orchestration. 
  - This project uses Airflow, but orchestration is loosely coupled, and the orchestration tool can be substituted.  

---

## Project Structure

```bash
airflow/                # Orchestration DAGs for calling Python scripts and running Bash commands
  dags/
src/
  api_ingestion/        # Scripts for fetching raw data from APIs
  config/               # App level configuration settings and credentials (e.g., API base URLs, region codes, project root)
  utils/                # Logging, file utilities, date helpers, cloud storage connection helpers
  data_modeling/        # SQL scripts for Silver cleaning + Gold transformations
                        # dbt project for Silver/Gold transformations
tests/                  # Unit and integration tests

MinIO                   # For raw file storage
DuckDB                  # Analytical engine for data transformations and processing
