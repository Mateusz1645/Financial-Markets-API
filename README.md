# financial-markets-api

## Table of Contents
- [Overview](#Overview)
- [Technology Stack](#technology-stack)
- [Running the Project](#running-the-project)
- [Docker Setup](#docker-setup)
- [Database](#database)
- [Application Lifecycle](#application-lifecycle)
- [API Modules](#api-modules)
  - [Assets / Portfolio](#assets--portfolio)
  - [Equities](#equities)
  - [Inflation](#inflation)
  - [Forex](#forex)
- [Data Models](#data-models)
- [Portfolio Upload](#portfolio-upload)
- [Authentication](#authentication)


## Overview

**financial-markets-api** is a backend API for **portfolio analysis and management of financial instruments**.  
It allows users to upload, manage, and analyze an investment portfolio using market data such as equities, forex rates, and inflation.

The API supports:
- uploading a portfolio from **CSV or Excel**
- manual asset management via endpoints
- portfolio valuation
- access to market reference data (equities, forex, inflation)

This project is intended for:
- portfolio analytics
- educational purposes
- internal analytical tools

---

## Technology Stack

- **Python 3.11**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL 16**
- **Docker / Docker Compose**
- OpenAPI 3.1 (Swagger UI)

---

## Running the Project

### Start with Docker Compose

```bash
docker compose up --build
```
After startup, the API will be available at:
```
http://localhost:8000
```
Swagger UI:
```
http://localhost:8000/
```

## Docker Setup
### Dockerfile
```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
Notes:
  - Uses a lightweight Python 3.11 image
  - Installs dependencies from requirements.txt
  - Runs FastAPI with uvicorn
  - --reload is intended for development only

## Database

The application uses **PostgreSQL 16** running in a **Docker container**.

### Default configuration

| Setting   | Value       |
|----------|-------------|
| User     | `postgres`  |
| Password | `postgres`  |
| Database | `portfolio` |
| Port     | `5432`      |

Database data is persisted using **Docker volumes**.

## Application Lifecycle

On application startup:

- waits for the database connection
- creates all database tables
- loads inflation data from a custom CSV file
- imports reference market data:
  - equities
  - forex rates

This logic is handled via FastAPI lifespan.

## API Modules

### Assets / Portfolio

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/assets/upload` | Upload portfolio from CSV or Excel |
| POST | `/assets/add` | Add a single asset manually |
| DELETE | `/assets/delete` | Delete an asset |
| GET | `/assets/list` | List all assets |
| GET | `/assets/choices` | Available asset choices |
| GET | `/assets/calc_current_value` | Calculate current asset value |

### Equities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/equities/list` | List equities |
| POST | `/equities/add` | Add equity |
| DELETE | `/equities/delete` | Delete equity |
| GET | `/equities/get_symbol` | Get symbol by ISIN |

### Inflation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inflation/list` | List inflation data |
| POST | `/inflation/add` | Add inflation record |
| DELETE | `/inflation/delete` | Delete inflation record |

### Forex

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forex/list` | List forex rates |

## Data Models

### Asset

Represents a single portfolio position.

**Key fields:**
- ISIN
- name
- amount
- transaction price
- currency
- asset type (e.g. equity, bond)

---

### Equity

Represents a market instrument (e.g. stock).

**Includes:**
- symbol (unique)
- ISIN
- sector and industry
- exchange and market
- country and company metadata

---

### Inflation

Stores monthly inflation values.

**Fields:**
- year
- month
- value

---

### Forex

Represents foreign exchange rates.

**Fields:**
- base currency
- quote currency
- value
- date

## Portfolio Upload

A sample input file is included in the project and can be used with:

`POST /assets/upload`

Supported formats:
- CSV
- Excel (.xlsx)

---

## Authentication

Currently:
  - No authentication

This project is intended for local or internal use only, so authentication is not implemented yet.
