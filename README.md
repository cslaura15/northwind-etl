# Data-Engineering-Expert-Practical-Case-Study

## Prerequisites

Before setting up the environment, make sure you have the following installed and running:

- **Docker Engine** (20.10+) and **Docker Compose v2** — everything in this project runs in containers, so no local Python installation is required
- **Git**, to clone the repository
- **At least 4 GB of RAM and 2 CPUs allocated to Docker**, and 10 GB of free disk space — the `airflow-init` container checks this on startup and will warn you if resources are too low
- **Ports 8080 and 5432 (or your configured `POSTGRES_DST_PORT`) free** on your machine — used by the Airflow UI and the destination Postgres database

> On Windows, run everything through **WSL2** — the entrypoint scripts in this project are bash-based and won't work in PowerShell/CMD directly.

Once these are in place, continue to [Environment Setup](#environment-setup) below.

## Getting Started

### Environment Variables

This project uses a `.env` file for configuration (Airflow settings, Postgres credentials, etc.). It is **not** committed to the repo since it contains secrets.

1. Copy the template to create the .env file and then modify it based on the next steps:
```bash
   # On Linux:
   cp env-template .env
```
2. On Linux, set `AIRFLOW_UID` to your host user ID to avoid file permission issues. To get your host user ID, run:
```bash
   id -u
```
3. Set the OpenWeatherMap API key. To obtain one, go to [openweather.org](https://openweathermap.org/) and click 'Get API Key'.

### Setting Up the Containers

```bash
# Build custom Airflow image (installs extra Python packages)
docker compose build

# Start all services in the background
docker compose up -d
```
One-liner:
```bash
docker compose build && docker compose up -d
```

### Accessing the Airflow UI

Once the containers are up, open the [Airflow GUI](http://localhost:8080) 

Login with the credentials set in `.env` (`_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD`, default `airflow` / `airflow`).  

### Stopping the Environment

```bash
docker compose down       # stop & remove containers, keep data
docker compose down -v    # stop & remove containers AND volumes (wipes data)
```

## Running the ETL pipeline

On the [Airflow GUI](http://localhost:8080), click on Dags >> northwind_etl. On the upper right corner, click on the `Trigger` button, then again, click on the `Trigger` button.