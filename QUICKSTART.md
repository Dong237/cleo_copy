# 🚀 Cleo Financial Assistant - Quickstart Guide

Get Cleo running locally in under 10 minutes!

## Prerequisites

Before you begin, ensure you have:
- **Docker** (v20.0+) and **Docker Compose** (v2.0+)
- **Git**
- At least **4GB RAM** available for Docker
- Ports 5432, 6379, 8001-8005 available

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cleo_copy
```

### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Create `.env` file from template
- Create necessary directories
- Start PostgreSQL and Redis
- Run database migrations

### 3. Start All Services

```bash
docker-compose up
```

Wait for all services to start (about 2-3 minutes first time).

### 4. Verify Services are Running

Open your browser and check:

- ✅ **User Service**: http://localhost:8001/docs
- ✅ **Banking Service**: http://localhost:8002/docs
- ✅ **Budget Service**: http://localhost:8003/docs
- ✅ **Chat Service**: http://localhost:8004/docs
- ✅ **Savings Service**: http://localhost:8005/docs
- ✅ **pgAdmin**: http://localhost:5050

## Testing the API

### Option 1: Using Swagger UI

Visit any service's `/docs` endpoint (e.g., http://localhost:8001/docs) for interactive API documentation.

### Option 2: Using cURL

#### 1. Register a New User

```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@cleo.ai",
    "password": "SecurePass123",
    "first_name": "Demo",
    "last_name": "User"
  }'
```

#### 2. Login

```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@cleo.ai",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from the response!

#### 3. Get User Profile

```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. Link Bank Account (Mock Plaid)

```bash
curl -X POST "http://localhost:8002/api/v1/plaid/exchange-token" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "mock-public-token-123"
  }'
```

#### 5. Get Transactions

```bash
curl -X GET "http://localhost:8002/api/v1/transactions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 6. Create a Budget

```bash
curl -X POST "http://localhost:8003/api/v1/budgets" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Food & Dining",
    "category": "food_dining",
    "amount": 500,
    "period": "monthly",
    "start_date": "2025-11-01",
    "end_date": "2025-11-30"
  }'
```

#### 7. Chat with Cleo

```bash
curl -X POST "http://localhost:8004/api/v1/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much did I spend this month?"
  }'
```

#### 8. Create Savings Goal

```bash
curl -X POST "http://localhost:8005/api/v1/savings/goals" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emergency Fund",
    "goal_type": "emergency_fund",
    "target_amount": 5000,
    "target_date": "2026-12-31",
    "autosave_enabled": true,
    "autosave_amount": 50,
    "autosave_frequency": "weekly"
  }'
```

## Service Ports Reference

| Service | Port | Swagger UI |
|---------|------|------------|
| User Service | 8001 | http://localhost:8001/docs |
| Banking Service | 8002 | http://localhost:8002/docs |
| Budget Service | 8003 | http://localhost:8003/docs |
| Chat Service | 8004 | http://localhost:8004/docs |
| Savings Service | 8005 | http://localhost:8005/docs |
| PostgreSQL | 5432 | - |
| Redis | 6379 | - |
| RabbitMQ Management | 15672 | http://localhost:15672 (guest/guest) |
| pgAdmin | 5050 | http://localhost:5050 (admin@cleo.local/admin) |

## Common Tasks

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove Data (Fresh Start)

```bash
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f user-service
```

### Rebuild Services

```bash
docker-compose build
docker-compose up
```

### Access Database

```bash
# Via psql
docker-compose exec postgres psql -U cleo -d cleo_db

# Via pgAdmin
# Open http://localhost:5050
# Login: admin@cleo.local / admin
# Add server: Host=postgres, Port=5432, User=cleo, Password=cleo_password
```

### Run Database Migrations

```bash
./scripts/run-migrations.sh
```

## Troubleshooting

### Port Already in Use

If you see "port is already allocated":

```bash
# Find and kill process using the port (example for 8001)
lsof -ti:8001 | xargs kill -9
```

### Services Won't Start

```bash
# Check Docker logs
docker-compose logs

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop # Mac/Windows
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Cannot Import Shared Modules

Make sure shared modules are properly mounted in docker-compose.yml:

```yaml
volumes:
  - ./backend/services/your-service:/app
  - ./backend/shared:/app/shared  # This line is critical!
```

## What's Included?

### ✅ 4 Core Microservices

1. **User Service** - Authentication, profiles, settings
2. **Banking Service** - Plaid integration, transactions, analytics
3. **Budget Service** - Budget management, tracking, insights
4. **Chat Service** - AI assistant with 4 personality modes
5. **Savings Service** - Goals, autosave, recommendations

### ✅ Full Database Schema

- 11 SQL schema files with all tables
- Users, accounts, transactions, budgets, savings, etc.
- Proper indexes and relationships

### ✅ Development Tools

- Swagger UI on all services
- pgAdmin for database management
- RabbitMQ management UI
- Hot reload for code changes

### ✅ Mock Data

- All services work with mock data
- No external API keys needed for testing
- Production-ready structure

## Next Steps

1. **Explore the APIs**: Visit each service's Swagger UI
2. **Read the Documentation**: Check `docs/API.md` for detailed endpoint info
3. **Add Your API Keys**: Update `.env` with real Plaid, OpenAI keys
4. **Build Mobile Apps**: See `mobile/ios/README.md` and `mobile/android/README.md`
5. **Run Tests**: `pytest` in backend services
6. **Deploy**: Follow `docs/DEPLOYMENT.md` for production deployment

## Get Help

- **Documentation**: See `/docs` folder
- **Issues**: Create an issue on GitHub
- **API Docs**: http://localhost:8001/docs (Swagger UI)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Mobile Apps                          │
│                    (iOS/Android - Coming)                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong)                      │
│                    http://localhost:8000                     │
└──────┬──────┬──────┬───────┬───────┬──────────────────────┬─┘
       │      │      │       │       │                       │
       ▼      ▼      ▼       ▼       ▼                       ▼
    ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌─────┐               ┌─────────┐
    │User│ │Bank│ │Budg│ │Chat│ │Save │               │Notif│...│
    │8001│ │8002│ │8003│ │8004│ │8005 │               │(TBD)│   │
    └──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘ └──┬──┘               └─────┘   │
       │      │      │       │       │                            │
       └──────┴──────┴───────┴───────┴────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
         ┌─────────────┐          ┌──────────┐
         │ PostgreSQL  │          │  Redis   │
         │    :5432    │          │  :6379   │
         └─────────────┘          └──────────┘
```

## License

[License TBD]

---

**Happy Coding! 🎉**

If you build something cool with Cleo, let us know!
