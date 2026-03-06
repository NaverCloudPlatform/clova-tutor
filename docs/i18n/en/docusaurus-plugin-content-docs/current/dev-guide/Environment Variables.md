---
slug: environment-variables
sidebar_position: 2
---

# Environment Variables

Create a `.env` file by copying `.env.example`, then configure the environment variables as described below.

```bash
cp .env.example .env
```

---

## Required Environment Variables

The following variables **must be set** in order to run the service locally.

### CLOVA Studio

> Refer to the [official CLOVA Studio documentation](https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary) for instructions on issuing API keys.

| Variable | Description |
|----------|-------------|
| `HCX_API_KEY` | HyperCLOVA X API key |
| `CLOVA_STUDIO_URL` | CLOVA Studio API endpoint URL |
| `CLOVA_STUDIO_HOST` | CLOVA Studio host |
| `CLOVA_STUDIO_API_KEY` | CLOVA Studio API key |
| `CLOVA_STUDIO_GW_API_KEY` | CLOVA Studio Gateway API key |
| `CLOVA_STUDIO_REQUEST_ID` | CLOVA Studio request ID |
| `CLOVA_STUDIO_APP_ID` | CLOVA Studio application ID |

### Swagger UI

| Variable | Description |
|----------|-------------|
| `SWAGGER_USERNAME` | Username for Swagger UI access |
| `SWAGGER_PASSWORD` | Password for Swagger UI access |

### Internal API

| Variable | Description | Example |
|----------|-------------|---------|
| `INTERNAL_API_KEY` | Authentication key for the internal problem registration API. Any arbitrary string may be used. | `my-secret-api-key-1234` |

### Local Storage (Security)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key used for URL signing. Any sufficiently random string may be used. | `my-secret-key-5678` |

---

## Optional Environment Variables

The following variables have default values and may be overridden depending on the deployment environment.

### General

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Application runtime environment | `LOCAL` |
| `STORAGE` | Storage backend type | `LOCAL` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

### Database (MySQL)

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_USER` | MySQL username | `local` |
| `MYSQL_PASSWORD` | MySQL password | `local_password` |
| `MYSQL_HOST` | MySQL host | `0.0.0.0` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_DB` | Database name | `local` |

### Redis

| Variable | Description | Default |
|----------|-------------|---------|
| `RC_SEED_URL` | Redis cluster seed URL | `redis:6379` |
| `RC_PASSWORD` | Redis password | `local_password` |
| `RC_TTL` | Redis TTL (in seconds) | `3600` |

### Weaviate (Vector Database)

| Variable | Description | Default |
|----------|-------------|---------|
| `WEAVIATE_HOST` | Weaviate host | `localhost` |
| `WEAVIATE_PORT` | Weaviate port | `8081` |
| `PROBLEM_INDEX` | Problem index name | `Problem_opensource` |
| `CURRICULUM_INDEX` | Curriculum index name | `Curriculum_opensource` |

### Model Server

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_SERVER_GRPC_URL` | gRPC endpoint of the model server | `edu-model-server:8051` |
| `RESPONSE_MODEL` | Model used for response generation | `hcx-005` |
| `GRPC_PORT` | gRPC port | `8051` |
| `EMBEDDING_TYPE` | Embedding provider type | `clovastudio` |

### Local Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_DIR` | Directory for uploaded files | `static` |
| `URL_EXPIRY_SECONDS` | Signed URL expiration time (seconds) | `3600` |
| `BASE_URL` | Base API URL | `http://localhost:8000/api/v1` |

### Server URLs

| Variable | Description | Default |
|----------|-------------|---------|
| `DATA_SERVER_URL` | Data server API URL | `http://localhost:8001/api/v1` |
| `BE_SERVER_URL` | Backend server API URL | `http://localhost:8000/api/v1` |
