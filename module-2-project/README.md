# Olist E-Commerce Data Engineering Pipeline

## 1. Project Overview

This project implements an end-to-end data engineering pipeline using the **Brazilian E-Commerce (Olist) dataset**.

The pipeline demonstrates how raw data can be extracted from a public data source, stored in cloud object storage, loaded into a data warehouse, transformed into analytics-ready models, orchestrated using Dagster, and finally presented through an interactive Streamlit dashboard.

### End-to-End Architecture

```text
Kaggle
   │
   ▼
Python Extraction Script
(Local PC)
   │
   │ CSV files
   ▼
Google Cloud Storage (GCS)
   │
   │ Raw data
   ▼
BigQuery
   │
   │ Raw / structured tables
   ▼
dbt
   │
   │ Analytics models
   ▼
Dagster
   │
   │ Orchestration & monitoring
   ▼
Streamlit
   │
   ▼
Analytics Dashboard
```

The application components are containerised using **Docker** and deployed on a VM. Source code is maintained in GitHub.

---

# 2. Technology Stack

| Component        | Technology           | Purpose                                              |
| ---------------- | -------------------- | ---------------------------------------------------- |
| Data Source      | Kaggle               | Source of the Olist e-commerce dataset               |
| Extraction       | Python               | Download and extract dataset files                   |
| Object Storage   | Google Cloud Storage | Store raw CSV files                                  |
| Data Warehouse   | BigQuery             | Store and query structured data                      |
| Transformation   | dbt                  | Transform raw data into analytical models            |
| Orchestration    | Dagster              | Schedule, orchestrate and monitor pipeline execution |
| Dashboard        | Streamlit            | Visualise analytical results                         |
| Containerisation | Docker               | Provide a reproducible runtime environment           |
| Source Control   | GitHub               | Store and version project code                       |
| Cloud Platform   | Google Cloud         | GCS and BigQuery infrastructure                      |

---

# 3. High-Level Pipeline Stages

## Stage 1 – Obtain the Dataset from Kaggle

The Olist Brazilian E-Commerce dataset is obtained from Kaggle.

The dataset contains multiple related CSV files, including:

* Orders
* Order items
* Customers
* Products
* Sellers
* Payments
* Reviews
* Geolocation

The initial objective is to obtain the raw source files without applying analytical transformations.

---

## Stage 2 – Python Data Extraction

A Python extraction script is used to download the Kaggle dataset.

The extraction layer is responsible for:

1. Connecting to Kaggle.
2. Downloading the dataset.
3. Extracting the required files.
4. Identifying the CSV files.
5. Preparing the files for cloud upload.

Example project structure:

```text
src/
└── extract/
    └── kaggle_extract.py
```

The extraction script can be developed and tested on the local PC.

The output of this stage is a collection of raw CSV files.

```text
Python Extraction
       │
       ▼
CSV files
```

---

# 4. Stage 3 – Load Raw Data into Google Cloud Storage

The extracted CSV files are uploaded to a Google Cloud Storage bucket.

The bucket acts as the **raw/landing layer** of the pipeline.

Example:

```text
GCS Bucket
└── raw/
    └── kaggle/
        ├── orders.csv
        ├── order_items.csv
        ├── customers.csv
        ├── products.csv
        └── ...
```

The raw files are retained in GCS so that the original extracted data is available independently of downstream transformations.

### Why GCS?

GCS provides:

* Durable cloud storage
* Separation between raw data and processing
* Easy integration with BigQuery
* A scalable landing zone for future datasets

---

# 5. Stage 4 – Load Data into BigQuery

The CSV files stored in GCS are loaded into BigQuery.

BigQuery becomes the central analytical data warehouse.

The initial layer contains raw or minimally processed tables.

Example:

```text
GCS
 │
 │ CSV
 ▼
BigQuery
 │
 └── olist_raw
      ├── orders
      ├── order_items
      ├── customers
      ├── products
      └── ...
```

The data can then be profiled to understand:

* Row counts
* Null values
* Duplicate records
* Data types
* Status distributions
* Date ranges
* Relationships between tables

For example, the orders dataset can be examined for:

```text
Total orders
Order status distribution
Delivery information
Order dates
Customer relationships
```

This profiling stage provides the foundation for designing the transformation models.

---

# 6. Stage 5 – Transform Data Using dbt

dbt is used to transform the raw BigQuery data into analytics-ready models.

The dbt project contains SQL models describing how the raw tables should be transformed.

Example:

```text
dbt/
└── olist_dbt/
    ├── models/
    │   ├── staging/
    │   ├── intermediate/
    │   └── marts/
    ├── dbt_project.yml
    └── profiles.yml
```

The transformation process can be conceptually divided into:

```text
Raw Tables
    │
    ▼
Staging Models
    │
    ▼
Intermediate Models
    │
    ▼
Analytics / Mart Models
```

### Staging

Staging models provide a clean and consistent representation of the raw source tables.

Typical activities include:

* Renaming columns
* Casting data types
* Standardising fields
* Basic cleaning

### Intermediate

Intermediate models combine and prepare data for business-level analysis.

Examples:

```text
orders + order_items
orders + customers
orders + products
```

### Mart / Analytics Layer

The final models are designed specifically for analytical queries and dashboard consumption.

Examples of possible analytical datasets include:

* Monthly order volume
* Sales by category
* Revenue trends
* Customer analysis
* Seller performance
* Delivery performance

---

# 7. dbt Manifest

dbt generates metadata about the project, including:

```text
target/manifest.json
```

The manifest describes the dbt project, including its models, dependencies and metadata.

Dagster uses this manifest when loading dbt assets.

Therefore, the deployment flow must ensure that the dbt project is parsed or compiled before Dagster attempts to load the dbt assets.

Conceptually:

```text
dbt project
     │
     ▼
dbt parse / compile
     │
     ▼
manifest.json
     │
     ▼
Dagster
```

The `target/` directory contains generated artifacts and normally should not be treated as source code that needs to be maintained manually in GitHub.

---

# 8. Stage 6 – Orchestration with Dagster

Dagster provides orchestration for the data pipeline.

Instead of manually running each transformation, Dagster provides a central place to define and execute the pipeline.

The Dagster project contains:

```text
dagster/
└── definitions.py
```

Dagster can represent the pipeline as assets and dependencies.

Conceptually:

```text
GCS
 │
 ▼
BigQuery Raw
 │
 ▼
dbt Staging
 │
 ▼
dbt Intermediate
 │
 ▼
dbt Marts
 │
 ▼
Dashboard Data
```

Dagster provides:

* Asset-based orchestration
* Dependency management
* Pipeline execution
* Run history
* Scheduling
* Monitoring
* Failure visibility

The Dagster UI is exposed on:

```text
http://<VM-IP>:3000
```

---

# 9. Stage 7 – Streamlit Dashboard

Streamlit provides the presentation layer.

The dashboard reads the analytical data produced by the BigQuery/dbt layer and presents it through interactive visualisations.

Conceptually:

```text
BigQuery Analytics Models
          │
          ▼
      Streamlit
          │
          ▼
    Interactive Dashboard
```

The dashboard can expose metrics such as:

* Total orders
* Sales trends
* Monthly order volume
* Product/category performance
* Customer analysis
* Seller performance
* Delivery metrics

The Streamlit application is exposed on:

```text
http://<VM-IP>:8501
```

---

# 10. Docker Containerisation

The application environment is containerised using Docker.

The purpose of Docker is to provide a consistent runtime environment containing the required tools and Python dependencies.

The container includes components such as:

```text
Docker Container
│
├── Python
├── Google Cloud libraries
├── dbt
├── Dagster
├── Streamlit
└── Project source code
```

This avoids depending on the exact Python/package configuration of the host machine.

The project can therefore be moved between development and deployment environments with much less configuration effort.

---

# 11. GitHub Source Control

The project source code is maintained in GitHub.

The repository contains the application and pipeline code, including:

```text
module-2-project/
│
├── src/
│   └── extract/
│       └── kaggle_extract.py
│
├── dbt/
│   └── olist_dbt/
│
├── dagster/
│   └── definitions.py
│
├── streamlit/
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

The VM obtains the project from GitHub.

The deployment flow is therefore:

```text
Developer
   │
   │ git push
   ▼
GitHub Repository
   │
   │ git pull / clone
   ▼
VM
   │
   ▼
Docker Container
```

This separates **source code** from **generated runtime artifacts**.

---

# 12. Deployment Environment

The production-like environment uses a VM running Docker.

The repository is pulled onto the VM and mounted into the Docker container.

Conceptually:

```text
                VM
┌───────────────────────────────────────┐
│                                       │
│  GitHub Repository                    │
│          │                            │
│          ▼                            │
│  Project Directory                   │
│          │                            │
│          │ Docker volume mount       │
│          ▼                            │
│  ┌─────────────────────────────────┐ │
│  │       Docker Container          │ │
│  │                                 │ │
│  │  Python                         │ │
│  │  dbt                            │ │
│  │  Dagster ──────── Port 3000    │ │
│  │  Streamlit ────── Port 8501    │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                       │
└───────────────────────────────────────┘
```

---

# 13. Configuration and Credentials

Cloud resources are accessed using environment variables and Google Cloud service-account credentials.

Typical configuration includes:

```text
GCP_PROJECT_ID
GCS_BUCKET_NAME
GOOGLE_APPLICATION_CREDENTIALS
```

Sensitive credentials should **not** be committed to GitHub.

For example:

```text
.env
service-account.json
```

should be excluded through `.gitignore`.

The deployment environment supplies these values securely to the container.

---

# 14. Pipeline Automation

The final objective is to move from manually executing individual commands to an automated pipeline.

The desired execution flow is:

```text
Pipeline Trigger
       │
       ▼
Extract / Load
       │
       ▼
GCS
       │
       ▼
BigQuery
       │
       ▼
dbt transformations
       │
       ▼
Dagster
       │
       ▼
Analytics tables
       │
       ▼
Streamlit Dashboard
```

Dagster provides the orchestration layer for scheduled and dependency-driven execution.

Instead of manually running every stage, dependencies can be represented within Dagster so that downstream assets execute after their upstream dependencies are available.

---

# 15. Development vs Deployment

The project uses two environments for different purposes.

### Local PC

Used primarily for:

* Development
* Testing Python extraction scripts
* Testing dbt models
* Developing the Streamlit application
* Testing changes before committing

```text
Local PC
 ├── Python
 ├── Git
 └── Project development
```

### VM / Docker

Used as the reproducible execution environment.

```text
VM
 │
 └── Docker
      ├── Python
      ├── dbt
      ├── Dagster
      └── Streamlit
```

This separation allows development to happen locally while providing a consistent runtime environment for the deployed pipeline.

---

# 16. End-to-End Implementation Steps

The architecture can be realised through the following high-level steps:

### Step 1 – Prepare the source

Obtain the Olist dataset from Kaggle.

### Step 2 – Develop the extraction layer

Create a Python script that downloads and prepares the CSV files.

### Step 3 – Create cloud storage

Create the Google Cloud Storage bucket and define the raw-data location.

### Step 4 – Upload raw data

Use Python/Google Cloud libraries to upload the extracted CSV files to:

```text
gs://<bucket>/raw/kaggle/
```

### Step 5 – Create BigQuery tables

Load the raw CSV files from GCS into BigQuery.

### Step 6 – Profile the raw data

Analyse the BigQuery tables for:

* Data quality
* Missing values
* Duplicates
* Row counts
* Relationships
* Distribution of important fields

### Step 7 – Build dbt models

Create:

```text
staging
    ↓
intermediate
    ↓
marts
```

and test the resulting models.

### Step 8 – Generate dbt artifacts

Run dbt parsing/compilation so that:

```text
target/manifest.json
```

is available to Dagster.

### Step 9 – Integrate dbt with Dagster

Define the dbt assets in:

```text
dagster/definitions.py
```

and configure their dependencies.

### Step 10 – Containerise the application

Build the Docker image containing the required Python, dbt, Dagster and Streamlit dependencies.

### Step 11 – Deploy to the VM

Pull the project from GitHub and start the Docker environment.

### Step 12 – Run Dagster

Use Dagster to orchestrate and monitor the pipeline.

Dagster UI:

```text
Port 3000
```

### Step 13 – Run Streamlit

Expose the analytical dashboard.

Streamlit:

```text
Port 8501
```

### Step 14 – Automate

Configure Dagster schedules or sensors so that the pipeline can execute automatically according to the required schedule.

---

# 17. Final Architecture

The complete architecture can be summarised as:

```text
                         DATA ENGINEERING PIPELINE
┌────────────┐
│   Kaggle   │
│ Data Source│
└─────┬──────┘
      │
      ▼
┌──────────────────────┐
│ Python Extraction    │
│ Script                │
│ Local PC              │
└─────┬────────────────┘
      │ CSV
      ▼
┌──────────────────────┐
│ Google Cloud Storage  │
│ Raw / Landing Zone    │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│ BigQuery              │
│ Raw Data Layer        │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│ dbt                   │
│ Staging               │
│ Intermediate          │
│ Marts                 │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│ Dagster               │
│ Orchestration         │
│ Scheduling             │
│ Monitoring             │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│ Streamlit             │
│ Analytics Dashboard   │
└──────────────────────┘


        Deployment Environment
┌────────────────────────────────────────┐
│              VM                         │
│                                        │
│  GitHub → Project → Docker Container  │
│                         │              │
│                         ├─ Dagster :3000│
│                         └─ Streamlit:8501│
│                                        │
└────────────────────────────────────────┘
```

---

# 18. Key Design Principles

The project demonstrates several important data engineering principles:

### Separation of concerns

Each component has a specific responsibility:

```text
Python  → Extraction
GCS     → Raw storage
BigQuery→ Data warehouse
dbt     → Transformation
Dagster → Orchestration
Streamlit → Presentation
Docker  → Runtime environment
GitHub  → Source control
```

### Raw data preservation

Raw files are retained in GCS before transformation.

### Reproducibility

Docker provides a consistent execution environment.

### Version control

Application and pipeline code are maintained in GitHub.

### Automated orchestration

Dagster provides dependency management, scheduling and monitoring.

### Separation of transformation and orchestration

dbt defines **how the data is transformed**, while Dagster manages **when and in what dependency order the transformations execute**.

---

# 19. Final Outcome

The completed project provides an end-to-end data engineering solution:

```text
Kaggle
  ↓
Python Extraction
  ↓
GCS Raw Data
  ↓
BigQuery
  ↓
dbt Analytics Models
  ↓
Dagster Orchestration
  ↓
Streamlit Dashboard
```

with:

```text
GitHub
   ↓
VM
   ↓
Docker
   ↓
Dagster + dbt + Streamlit
```

This architecture demonstrates the complete lifecycle from **data extraction and cloud ingestion through transformation, orchestration and analytical visualisation**.
