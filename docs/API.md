# API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.cleo.ai/api/v1
```

## Authentication

Most endpoints require authentication using JWT tokens.

### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-11-13T10:00:00Z"
}
```

#### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

### User Management

#### Get Current User

```http
GET /users/me
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "personality_mode": "supportive",
  "subscription_tier": "free",
  "created_at": "2025-11-13T10:00:00Z"
}
```

#### Update User Profile

```http
PUT /users/me
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "phone_number": "+1234567890"
}
```

#### Update Personality Mode

```http
PUT /users/me/personality
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "personality_mode": "roast"
}
```

### Banking (Plaid Integration)

#### Link Bank Account

```http
POST /accounts/link
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "public_token": "public-sandbox-xxx",
  "account_id": "account-id-xxx"
}
```

#### Get Accounts

```http
GET /accounts
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "accounts": [
    {
      "id": "uuid",
      "account_name": "Chase Checking",
      "account_type": "checking",
      "current_balance": 2500.50,
      "available_balance": 2500.50,
      "currency": "USD",
      "institution_name": "Chase"
    }
  ]
}
```

#### Get Transactions

```http
GET /transactions?start_date=2025-10-01&end_date=2025-11-13
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "transactions": [
    {
      "id": "uuid",
      "amount": -45.50,
      "merchant_name": "Starbucks",
      "category_primary": "Food & Dining",
      "date": "2025-11-12",
      "pending": false
    }
  ],
  "total": 150
}
```

### Budgeting

#### Create Budget

```http
POST /budgets
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Eating Out Budget",
  "category": "restaurants",
  "amount": 300,
  "period": "monthly",
  "start_date": "2025-11-01",
  "end_date": "2025-11-30"
}
```

#### Get Budgets

```http
GET /budgets
Authorization: Bearer <token>
```

#### Get Budget Summary

```http
GET /budgets/summary?period=current
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total_budget": 2000,
  "total_spent": 1450,
  "remaining": 550,
  "percentage_used": 72.5,
  "categories": [
    {
      "category": "restaurants",
      "budget": 300,
      "spent": 285,
      "remaining": 15,
      "percentage": 95
    }
  ]
}
```

### Savings

#### Create Savings Goal

```http
POST /savings/goals
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Emergency Fund",
  "goal_type": "emergency_fund",
  "target_amount": 5000,
  "target_date": "2026-12-31",
  "autosave_enabled": true,
  "autosave_amount": 50,
  "autosave_frequency": "weekly"
}
```

#### Get Savings Goals

```http
GET /savings/goals
Authorization: Bearer <token>
```

#### Add to Savings

```http
POST /savings/deposit
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "goal_id": "uuid",
  "amount": 100,
  "method": "manual"
}
```

### Chat (AI Assistant)

#### Send Message

```http
POST /chat/message
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "message": "How much did I spend on food this month?",
  "conversation_id": "uuid" // optional
}
```

**Response:** `200 OK`
```json
{
  "conversation_id": "uuid",
  "message": "You spent $450 on food this month, which is 15% more than last month. $285 was on restaurants and $165 on groceries.",
  "intent": "spending_query",
  "confidence": 0.95
}
```

### Cash Advances

#### Check Eligibility

```http
GET /advances/eligibility
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "is_eligible": true,
  "max_amount": 250,
  "reason": "Good income history and no recent overdrafts"
}
```

#### Request Advance

```http
POST /advances/request
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 100,
  "repayment_date": "2025-11-27",
  "delivery_method": "instant",
  "tip_amount": 5
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes:**
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - External service error

## Rate Limiting

- Most endpoints: 100 requests/minute
- AI/Chat endpoints: 50 requests/minute
- Headers returned:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Webhooks

Coming soon: Plaid webhooks for transaction updates, Stripe webhooks for payments.

---

For more details, see the interactive API documentation at `/docs` (Swagger UI) or `/redoc` when running the services locally.
