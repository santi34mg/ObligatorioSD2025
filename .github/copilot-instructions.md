# Copilot Instructions for ObligatorioSD2025

## Architecture Overview

This is a **microservices-based distributed system** ("UMShare" - university material sharing platform) with event-driven communication patterns:

- **Frontend**: React + TypeScript + Vite + Tailwind CSS (port 5173)
- **Backend Services**: FastAPI microservices with distinct data stores
- **API Gateway**: Traefik reverse proxy with service discovery
- **Message Broker**: RabbitMQ for async event-driven communication
- **Databases**: PostgreSQL (auth), MongoDB (content/collaboration), MinIO (object storage)

## Critical Architecture Patterns

### 1. Shared Module Pattern

All services import from `shared/` directory for cross-cutting concerns:

- `shared/rabbitmq_client.py` - Centralized RabbitMQ pub/sub client
- `shared/rabbitmq_config.py` - Event topology definitions (exchanges, queues, routing keys)
- `shared/websocket_client.py` - WebSocket client utilities

**Dockerfile Convention**: Services MUST copy `shared/` to work correctly:

```dockerfile
COPY shared/ ./shared/
```

### 2. Service Communication Patterns

- **Synchronous**: Direct HTTP via Traefik routing (`PathPrefix` rules)
- **Asynchronous**: RabbitMQ topic exchanges for event broadcasting
- **Real-time**: WebSocket service for live updates

**Event naming convention**: `{domain}.{action}` (e.g., `user.registered`, `content.created`)

- Each domain has dedicated exchange (e.g., `user.events`, `content.events`)
- Services subscribe to specific routing keys via RabbitMQ queues

### 3. Service Routing (Traefik)

Services are exposed via path-based routing on `localhost`:

- Frontend: `http://localhost` (root path)
- Auth: `http://localhost/auth/*`
- Collaboration: `http://localhost/collab/*`
- Moderation: `http://localhost/moderation/*`
- WebSocket: `http://localhost/ws/*`
- Communication: `http://localhost/communication/*`

**Dashboard**: Traefik dashboard at `http://localhost:8081`

## Service Details

### Auth Service (PostgreSQL)

- Uses `fastapi-users` library with SQLAlchemy ORM (async)
- JWT-based authentication with Bearer tokens
- Database: PostgreSQL with asyncpg driver
- Hardcoded SECRET in `users.py` - **DO NOT use in production**
- Entry point: `main.py` runs `app.app:app` with uvicorn

### Content Service (MongoDB + MinIO)

- Handles file uploads to MinIO object storage
- Metadata stored in MongoDB `umshare.materials` collection
- Entry point: `main.py` includes router from `app.app`

### Collaboration Service (MongoDB)

- Thread/comment system for discussions
- Uses Motor (async MongoDB driver)
- Authentication via headers (`X-User-Id`, `X-User-Name`) - temporary pattern
- Collections: `threads`, `comments` with text indexes

### Moderation Service

- Content moderation via `app/moderation.py`
- Text-based filtering (see `moderation.moderate_text()`)

### WebSocket Service

- Connection manager pattern for room-based broadcasting
- Supports personal messages and room-based communication
- CORS enabled for frontend integration

### Communication Service

- Basic WebSocket chat with broadcast pattern
- Simpler implementation than WebSocket service (candidate for consolidation)

## Development Workflows

### Starting the Stack

```bash
docker-compose up --build
```

### Working with Individual Services

Most services follow this structure:

```
services/<service-name>/
  ├── Dockerfile
  ├── main.py          # Entry point
  ├── requirements.txt
  └── app/
      ├── app.py       # FastAPI app & routes
      ├── db.py        # Database setup
      └── schemas.py   # Pydantic models
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev  # Runs on port 5173
```

### Database Access

- PostgreSQL: `localhost:5432` (postgres/postgres)
- MongoDB: `localhost:27017`
- MinIO: `localhost:9000` (minioadmin/minioadmin)
- RabbitMQ Management: `http://rabbitmq.localhost` (via Traefik)

## Project-Specific Conventions

### Authentication Pattern

- Auth service uses `fastapi-users` with pre-built routers
- Login: POST `application/x-www-form-urlencoded` to `/auth/jwt/login`
- Register: POST JSON to `/auth/register`
- Protected routes use `Depends(current_active_user)`

### Database Patterns

- **Async PostgreSQL**: SQLAlchemy + asyncpg
- **Async MongoDB**: Motor (AsyncIOMotorClient)
- DB initialization: Auth service creates tables in `create_db_and_tables()`
- MongoDB indexes created on first `get_db()` call

### Frontend API Calls

Frontend makes direct fetch calls to Traefik-routed endpoints:

```typescript
fetch("http://localhost/auth/register", { method: "POST", ... })
```

### RabbitMQ Integration

Services using RabbitMQ should:

1. Import `RabbitMQClient` from `shared.rabbitmq_client`
2. Initialize with service name: `RabbitMQClient(service_name="auth-service")`
3. Connect via `await client.connect()`
4. Publish events: `await client.publish_event(event_type, data)`

Currently only auth-service partially implements RabbitMQ (see `app.py` imports).

## Known Issues & TODOs

1. **Commented services** in docker-compose.yml - auth-service has two definitions (one commented)
2. **Hardcoded secrets**: JWT secret is `"SECRET"` in production code
3. **Temporary auth** in collaboration-service uses header-based user metadata
4. **Service consolidation**: communication-service and websocket-service have overlapping functionality
5. **Missing error handling**: Many endpoints lack proper exception handling
6. **No tests**: Project has no test suite

## Adding New Services

1. Create directory under `services/<new-service>/`
2. Add Dockerfile that copies `shared/` directory
3. Add FastAPI app with health check endpoint
4. Add Traefik labels to docker-compose.yml:
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.<service>.rule=PathPrefix(`/<path>`)"
     - "traefik.http.services.<service>.loadbalancer.server.port=8000"
   ```
5. Add network: `traefik`

## Key Files to Reference

- `shared/rabbitmq_config.py` - Complete event topology
- `services/auth-service/app/users.py` - fastapi-users setup pattern
- `services/collaboration-service/app/main.py` - Motor MongoDB pattern
- `docker-compose.yml` - Service orchestration and Traefik routing
- `traefik-config/traefik.yml` - Proxy configuration
