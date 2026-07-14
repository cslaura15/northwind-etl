# Data-Engineering-Expert-Practical-Case-Study

## Getting Started

### Environment Variables

This project uses a `.env` file for configuration (Airflow settings, Postgres credentials, etc.). It is **not** committed to the repo since it contains secrets.

1. Copy the template:
```bash
   cp env-template .env
```
2. On Linux, set `AIRFLOW_UID` to your host user ID to avoid file permission issues. To get your host user ID, run:
```bash
   id -u
```
3. Set the OpenWeatherMap API key. To obtain one, go to [openweather.org](https://openweathermap.org/) and click on 'Get API Key'.

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

