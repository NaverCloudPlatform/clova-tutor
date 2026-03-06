---
slug: quick-start
sidebar_position: 1
---

### Prerequisites

Before starting, make sure the following tools are installed on your system.

- [Docker](https://docs.docker.com/get-docker/) / [Docker Compose](https://docs.docker.com/compose/install/) — containerization platform
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python dependency management tool

---

### 0. Required environment setup

Create a `.env` file by copying `.env.example`, then configure the required environment variables.

```bash
cp .env.example .env
```

The following variables **must** be set:

- `HCX_API_KEY`
- All `CLOVA_STUDIO_*` related variables

> For a detailed description of each variable, see the [Environment Variables](./environment-variables) documentation.

---

### 1. Start the local environment

Start all required services using Docker Compose.

```bash
docker compose up -d
```

This will launch the backend, model server, and dependent services.

---

### 2. Backend initial setup

Initialize the backend with sample data and required internal state.

```bash
cd backend && make init
```

---

### 3. Model server initial setup

Set up the model server using sample data and default configurations.

```bash
cd model-server && make setup
```

---

### 4. Verify the services

Once all services are running, verify that each component is accessible.

- Web UI: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
