# Todo API

Todo API is a simple RESTful service for managing a to-do list, allowing users to create, read, update, and delete tasks.

## Prerequisites

- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/)

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/matheusgalvao1/todo-api.git
   cd todo-api
   ```

2. Build and start the application with Docker Compose:

   ```bash
   docker-compose up --build -d
   ```

3. The API will be available at `http://localhost:8000`.

## Authentication Methods

The API's authentication is configured through `auth_config.yml` in the root directory:

1. No Authentication (`none`):
   ```yaml
   auth:
     method: none
   ```
   All endpoints will be public.

2. API Key Authentication (`api_key`):
   ```yaml
   auth:
     method: api_key
     api_key: your-secure-api-key
   ```
   Clients must include the API key in the `X-API-Key` header.

3. JWT Authentication (`jwt`):
   ```yaml
   auth:
     method: jwt
     secret: your-jwt-secret
   ```
   Clients must obtain a JWT token via login/signup and include it in the `Authorization: Bearer <token>` header.

4. Session Authentication (`session`):
   ```yaml
   auth:
     method: session
     secret: your-session-secret
   ```
   Uses browser sessions for authentication.

## Running the API

Simply run:
```bash
python app/main.py
```

The API will read the configuration from `auth_config.yml`. If the file doesn't exist, it will default to no authentication.
