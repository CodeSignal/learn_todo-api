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

## Running the API

### Basic Usage (No Authentication)
Run the API with public access to all endpoints:
```bash
python app/main.py
```
This is equivalent to explicitly disabling auth:
```bash
python app/main.py --auth none
```

### Protected Mode
Enable authentication to protect all endpoints (except /auth and error handlers):

1. API Key authentication:
   ```bash
   python app/main.py --auth api_key --secret "your-secure-api-key"
   ```

2. JWT authentication:
   ```bash
   python app/main.py --auth jwt --secret "my-jwt-secret"
   ```

3. Session authentication:
   ```bash
   python app/main.py --auth session --secret "my-session-secret"
   ```

If you don't provide a secret, default values will be used, but this is not recommended for production.
