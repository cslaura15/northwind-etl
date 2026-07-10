# Data-Engineering-Expert-Practical-Case-Study

## Getting Started

### Environment Variables

This project uses a `.env` file for configuration (Airflow settings, Postgres credentials, etc.). It is **not** committed to the repo since it contains secrets.

1. Copy the template:
```bash
   cp env-template .env
```
2. Fill in the values (Fernet key, Postgres user/password, etc.). Generate a Fernet key with:
```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
3. On Linux, set `AIRFLOW_UID` to your host user ID to avoid file permission issues:
```bash
   echo "AIRFLOW_UID=$(id -u)" >> .env
```

### Setting Up the Containers

```bash
# Build custom Airflow image (installs extra Python packages)
docker compose build

# Initialize Airflow (creates metadata DB, admin user, sets permissions)
docker compose up airflow-init

# Start all services in the background
docker compose up -d
```

Check that everything is running:

```bash
docker compose ps
```

### Accessing the Airflow UI

Once the containers are up, open the [Airflow GUI](http://localhost:8080) 

Login with the credentials set in `.env` (`_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD`, default `airflow` / `airflow`).  

### Stopping the Environment

```bash
docker compose down       # stop & remove containers, keep data
docker compose down -v    # stop & remove containers AND volumes (wipes data)
```

