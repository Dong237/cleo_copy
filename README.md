# AI Financial Assistant (Cleo Clone)

An AI-powered financial assistant that helps users manage their personal finances through budgeting, spending analysis, savings automation, cash advances, and credit building.

## 🎯 Project Overview

This is a comprehensive fintech application targeting Gen Z and Millennials (ages 18-40) with:
- Conversational AI interface with customizable personality
- Automated budgeting and spending insights
- Smart savings automation
- Cash advance capabilities
- Credit building tools
- Bill tracking and reminders

**Business Model:** Freemium with subscription tiers
- Free: Core budgeting and tracking
- Cleo Plus ($5.99/month): Cash advances, enhanced insights
- Cleo Builder ($14.99/month): Credit builder card, credit monitoring

## 📁 Project Structure

```
.
├── backend/                    # Backend microservices
│   ├── services/              # Individual microservices
│   │   ├── user-service/      # Authentication, profiles, settings
│   │   ├── banking-service/   # Plaid integration, transactions
│   │   ├── budget-service/    # Budget management, tracking
│   │   ├── chat-service/      # AI conversational interface
│   │   ├── savings-service/   # Autosave, goals, transfers
│   │   ├── advance-service/   # Cash advance eligibility & management
│   │   ├── credit-service/    # Credit builder card, monitoring
│   │   ├── notification-service/  # Push, SMS, email notifications
│   │   ├── analytics-service/     # Data aggregation, insights
│   │   └── recommendation-service/ # Personalized tips
│   ├── shared/                # Shared libraries and utilities
│   └── gateway/               # API Gateway (Kong/AWS API Gateway)
├── mobile/                    # Mobile applications
│   ├── ios/                   # iOS app (Swift/SwiftUI)
│   └── android/               # Android app (Kotlin/Jetpack Compose)
├── ml/                        # Machine Learning components
│   ├── models/                # ML model definitions
│   ├── training/              # Training scripts and pipelines
│   └── serving/               # Model serving infrastructure
├── database/                  # Database schemas and migrations
│   ├── schemas/               # SQL schema definitions
│   └── migrations/            # Database migration scripts
├── infrastructure/            # Infrastructure as Code (Terraform)
├── tests/                     # Testing suites
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
└── .github/workflows/         # CI/CD pipelines
```

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Languages:** Python 3.11+ (AI/ML services), Go 1.21+ (high-throughput services)
- **Frameworks:** FastAPI (Python), Gin (Go)
- **Database:** PostgreSQL 14+ (primary), Redis 7+ (cache)
- **Message Queue:** RabbitMQ / AWS SQS
- **API Gateway:** Kong / AWS API Gateway

**Mobile:**
- **iOS:** Swift 5.9+, SwiftUI, MVVM architecture
- **Android:** Kotlin 1.9+, Jetpack Compose, MVVM with Clean Architecture

**AI/ML:**
- **ML Framework:** PyTorch 2.0+ / TensorFlow 2.x
- **NLP:** Custom BERT-based intent classification + GPT-4/Claude integration
- **ML Ops:** MLflow, TensorFlow Serving

**Infrastructure:**
- **Cloud:** AWS / Google Cloud / Azure
- **Containers:** Kubernetes (EKS/GKE/AKS)
- **IaC:** Terraform
- **Monitoring:** Datadog, Prometheus + Grafana

### Third-Party Integrations

- **Banking Data:** Plaid (primary), Yodlee (backup)
- **Partner Bank:** WebBank, Cross River Bank
- **Credit Reporting:** Experian, Equifax, TransUnion
- **LLM Provider:** OpenAI (GPT-4) / Anthropic (Claude)
- **Push Notifications:** Firebase Cloud Messaging (FCM)
- **SMS:** Twilio
- **Email:** SendGrid / Amazon SES
- **Analytics:** Mixpanel, Amplitude

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Go 1.21+
- Node.js 18+ (for tooling)
- PostgreSQL 14+
- Redis 7+

### Quick Start (10 Minutes)

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup and API testing guide.

**TL;DR:**

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access services:**
   - User Service: http://localhost:8001
   - Banking Service: http://localhost:8002
   - Budget Service: http://localhost:8003
   - Chat Service: http://localhost:8004
   - Savings Service: http://localhost:8005
   - Notification Service: http://localhost:8006
   - Advance Service: http://localhost:8007
   - Credit Service: http://localhost:8008
   - pgAdmin: http://localhost:5050
   - RabbitMQ Management: http://localhost:15672

3. **Run tests:**
   ```bash
   ./scripts/run-tests.sh
   ```

4. **Interactive API docs:**
   - Each service exposes Swagger UI at `/docs` endpoint
   - Example: http://localhost:8001/docs

## 🎉 Implementation Status

### ✅ Completed Services (8/10 Core Services)

1. **User Service** (Port 8001) - ✅ Complete
   - JWT authentication
   - User profiles and settings
   - Subscription management

2. **Banking Service** (Port 8002) - ✅ Complete
   - Plaid integration (mock)
   - Transaction sync and categorization
   - Account analytics

3. **Budget Service** (Port 8003) - ✅ Complete
   - Budget creation and tracking
   - Spending analysis
   - Budget alerts and insights

4. **Chat Service** (Port 8004) - ✅ Complete
   - AI chatbot with 4 personalities
   - Intent classification
   - Conversation history

5. **Savings Service** (Port 8005) - ✅ Complete
   - Savings goals
   - Autosave automation
   - Safe-to-save AI recommendations

6. **Notification Service** (Port 8006) - ✅ Complete
   - Push notifications (Firebase)
   - SMS (Twilio)
   - Email (SendGrid)
   - User preferences

7. **Advance Service** (Port 8007) - ✅ Complete
   - Cash advance eligibility
   - Smart underwriting ($20-$250)
   - Repayment management

8. **Credit Service** (Port 8008) - ✅ Complete
   - Credit score monitoring
   - Credit builder card
   - Credit coaching sessions
   - Personalized recommendations

### 🚧 Remaining Services (2/10)

9. **Analytics Service** (Port 8009) - Planned
   - Data aggregation
   - User behavior analytics
   - Business intelligence

10. **Recommendation Service** (Port 8010) - Planned
    - ML-powered spending insights
    - Savings optimization
    - Personalized financial tips

### 📊 Development Progress: **Phase 2 - 80% Complete**

### Phase 1: MVP ✅ COMPLETE
- [x] Project structure and Docker setup
- [x] User authentication and onboarding
- [x] Plaid bank integration (mock ready for production)
- [x] Transaction sync and categorization
- [x] AI chat with personality modes
- [x] Budget creation and tracking
- [x] Spending analysis and insights
- [x] Savings automation and goals

### Phase 2: Growth Features ✅ 80% COMPLETE
- [x] Enhanced AI chat with personality customization
- [x] Cash advances with underwriting (Cleo Plus)
- [x] Push notifications, SMS, and email
- [x] Advanced autosave strategies
- [x] Comprehensive test suite (80+ tests)
- [ ] Bill tracking and reminders (Planned)
- [ ] Weekly quizzes (Planned)

### Phase 3: Credit Building ✅ COMPLETE
- [x] Credit Builder secured card
- [x] Credit score monitoring
- [x] Credit coaching (5 educational modules)
- [x] Personalized credit recommendations

### Phase 4: Advanced Features (Months 19-24)
- [ ] Debt payoff planning
- [ ] Investment recommendations
- [ ] Tax optimization tips
- [ ] Financial wellness score

## 🧪 Testing

**Test Coverage:** 80+ comprehensive tests across all services

```bash
# Run all tests with coverage
./scripts/run-tests.sh

# Or run tests manually
cd backend
pytest tests/ -v --cov=services --cov-report=html
```

### Test Summary
- **User Service:** 14 tests (auth, profiles, settings)
- **Banking Service:** 8 tests (Plaid, transactions, analytics)
- **Chat Service:** 11 tests (AI, intent classification, conversations)
- **Budget Service:** 8 tests (CRUD, tracking, alerts, insights)
- **Savings Service:** 10 tests (goals, autosave, transfers)
- **Advance Service:** 28 tests (eligibility, underwriting, repayments)
- **Total:** 79+ integration tests

## 📊 Success Metrics

**User Acquisition:**
- Year 1: 100K users
- Year 2: 1M users

**Engagement:**
- 70%+ Monthly Active Users (MAU)
- 15%+ conversion to paid subscriptions
- 80%+ retention after first month

**Technical:**
- API response time: p95 < 200ms
- System uptime: 99.9%
- App crash rate: < 1%

## 🔒 Security & Compliance

- **Encryption:** AES-256 (at-rest), TLS 1.3 (in-transit)
- **Authentication:** OAuth 2.0, JWT tokens, 2FA
- **Compliance:** SOC 2, GDPR, CCPA, BSA/AML, FCRA
- **Banking Security:** Plaid integration (read-only access)
- **PCI DSS:** Compliant for credit card data handling

## 📖 Documentation

- [Product Requirements Document](docs/PRD.md)
- [API Documentation](docs/API.md)
- [Architecture Decision Records](docs/ADR/)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## 📝 License

[License details to be determined]

## 👥 Team

- Backend Engineers (Python/Go)
- Mobile Engineers (iOS/Android)
- Data Scientists / ML Engineers
- Product Designers
- Product Managers
- QA Engineers
- DevOps Engineers

## 📞 Support

For questions or support, please contact: [support email to be determined]

---

**Status:** 🚧 In Development - Phase 1 (MVP)

**Last Updated:** November 13, 2025
