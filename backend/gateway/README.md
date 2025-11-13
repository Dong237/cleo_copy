# API Gateway (Kong)

This directory contains configuration for the Kong API Gateway, which serves as the entry point for all client requests to the backend microservices.

## Features

- **Unified Entry Point:** Single endpoint for all API calls
- **Rate Limiting:** Protect services from abuse
- **CORS:** Cross-origin resource sharing configuration
- **Request/Response Transformation:** Modify requests/responses as needed
- **Authentication:** JWT token validation (to be implemented)
- **Monitoring:** Prometheus metrics for observability

## Configuration

The `kong.yml` file defines:
- Services (backend microservices)
- Routes (URL paths)
- Plugins (rate limiting, CORS, etc.)

## Admin API

Kong Admin API is available at `http://localhost:8002` (mapped to Kong's internal port 8001).

### Common Commands

```bash
# Check Kong status
curl http://localhost:8002/status

# List all services
curl http://localhost:8002/services

# List all routes
curl http://localhost:8002/routes

# Add a new plugin
curl -X POST http://localhost:8002/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100"
```

## Applying Configuration

To apply the Kong configuration from `kong.yml`:

```bash
# Using deck (Kong's declarative configuration tool)
deck sync --kong-addr http://localhost:8002
```

## Service URLs

When Kong is running, access services through:

- **Base URL:** `http://localhost:8000`
- **User Service:** `http://localhost:8000/api/v1/auth`, `/api/v1/users`
- **Banking Service:** `http://localhost:8000/api/v1/accounts`, `/api/v1/transactions`
- **Budget Service:** `http://localhost:8000/api/v1/budgets`
- **Chat Service:** `http://localhost:8000/api/v1/chat`

## Rate Limiting

Default rate limits:
- Most endpoints: 100 requests/minute, 1000 requests/hour
- AI/Chat endpoints: 50 requests/minute, 500 requests/hour

## Future Enhancements

- [ ] JWT authentication plugin
- [ ] Request validation
- [ ] Response caching
- [ ] API versioning
- [ ] Circuit breaker
- [ ] Request transformation
- [ ] Logging to external services
