# Deployment Guide

This guide covers deploying Cleo Financial Assistant to production.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] Database migrations prepared
- [ ] Monitoring and logging configured
- [ ] Backup strategy in place
- [ ] Rollback plan prepared
- [ ] Security scan completed
- [ ] Load testing completed

## Infrastructure Requirements

### Cloud Provider

Recommended: AWS, Google Cloud, or Azure

**Minimum Resources:**
- PostgreSQL: 2 vCPUs, 4GB RAM, 100GB SSD
- Redis: 1 vCPU, 2GB RAM
- Backend services: 2 vCPUs, 4GB RAM each (auto-scaling)
- Load Balancer: Application Load Balancer
- CDN: CloudFront, CloudFlare, or similar

### Kubernetes Cluster

**Production Cluster:**
- 3+ nodes for high availability
- Auto-scaling enabled
- Multiple availability zones
- Resource limits and requests configured

## Environment Setup

### 1. Configure Environment Variables

Create production `.env` file with secure values:

```bash
# NEVER commit this file
ENVIRONMENT=production
DEBUG=false

# Database (use RDS, Cloud SQL, etc.)
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/cleo_prod

# Redis (use ElastiCache, Memorystore, etc.)
REDIS_URL=redis://redis-host:6379/0

# Security (use strong, random keys)
SECRET_KEY=<generate-strong-key>

# API Keys (from secure vault)
PLAID_CLIENT_ID=<production-client-id>
PLAID_SECRET=<production-secret>
PLAID_ENV=production

OPENAI_API_KEY=<production-key>
TWILIO_ACCOUNT_SID=<production-sid>
SENDGRID_API_KEY=<production-key>

# Monitoring
SENTRY_DSN=<production-dsn>
```

### 2. Set Up Secrets Management

Use a secrets manager:
- **AWS:** AWS Secrets Manager
- **GCP:** Secret Manager
- **Azure:** Key Vault
- **Other:** HashiCorp Vault

```bash
# Example: AWS Secrets Manager
aws secretsmanager create-secret \
  --name cleo/production/database-url \
  --secret-string "postgresql://..."

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id cleo/production/database-url
```

## Database Deployment

### 1. Provision Database

**Option A: Managed Service (Recommended)**
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL

**Option B: Self-Managed**
- Deploy on Kubernetes with persistent volumes
- Set up replication and backups

### 2. Run Migrations

```bash
# Backup current database first!
pg_dump -h <host> -U <user> -d cleo_prod > backup_$(date +%F).sql

# Run migrations
for file in database/schemas/*.sql; do
  psql -h <host> -U <user> -d cleo_prod -f "$file"
done

# Verify
psql -h <host> -U <user> -d cleo_prod -c "\dt"
```

### 3. Set Up Backups

```bash
# Automated daily backups
# AWS RDS: Enable automated backups (7-35 days retention)
# GCP: Automated daily backups with point-in-time recovery
# Manual backup script:
0 2 * * * pg_dump -h <host> -U <user> cleo_prod | gzip > /backups/cleo_$(date +\%F).sql.gz
```

## Docker Image Building

### 1. Build Production Images

```bash
# Build and tag images
docker build -t cleo-user-service:v1.0.0 ./backend/services/user-service
docker build -t cleo-banking-service:v1.0.0 ./backend/services/banking-service
docker build -t cleo-budget-service:v1.0.0 ./backend/services/budget-service
docker build -t cleo-chat-service:v1.0.0 ./backend/services/chat-service

# Push to registry
docker tag cleo-user-service:v1.0.0 <registry>/cleo-user-service:v1.0.0
docker push <registry>/cleo-user-service:v1.0.0
```

### 2. Use CI/CD for Automated Builds

GitHub Actions workflow (already configured in `.github/workflows/ci.yml`) will:
- Run tests
- Build Docker images
- Push to container registry
- Deploy to Kubernetes

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

**Example: User Service Deployment**

```yaml
# k8s/user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: <registry>/cleo-user-service:v1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cleo-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: ClusterIP
```

### 2. Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/user-service

# Scale deployment
kubectl scale deployment user-service --replicas=5
```

### 3. Configure Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cleo-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.cleo.ai
    secretName: cleo-tls
  rules:
  - host: api.cleo.ai
    http:
      paths:
      - path: /api/v1/auth
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
      - path: /api/v1/accounts
        pathType: Prefix
        backend:
          service:
            name: banking-service
            port:
              number: 80
```

## Monitoring and Logging

### 1. Set Up Application Monitoring

**Datadog:**
```bash
# Install Datadog agent
kubectl apply -f https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/agent.yaml
```

**Prometheus + Grafana:**
```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus

# Install Grafana
helm install grafana grafana/grafana
```

### 2. Configure Logging

**ELK Stack:**
```bash
# Install Elasticsearch, Logstash, Kibana
helm install elasticsearch elastic/elasticsearch
helm install logstash elastic/logstash
helm install kibana elastic/kibana
```

**CloudWatch Logs (AWS):**
```bash
# Configure fluent-bit for log forwarding
kubectl apply -f k8s/logging/fluent-bit-configmap.yaml
```

### 3. Set Up Alerts

Configure alerts for:
- High error rates (> 1%)
- Slow response times (p95 > 500ms)
- Low success rates (< 99%)
- Database connection issues
- High CPU/memory usage (> 80%)
- Disk space (< 20% free)

## Mobile App Deployment

### iOS

1. **Build release version:**
   ```bash
   xcodebuild archive -workspace Cleo.xcworkspace -scheme Cleo -archivePath ./build/Cleo.xcarchive
   ```

2. **Export for App Store:**
   ```bash
   xcodebuild -exportArchive -archivePath ./build/Cleo.xcarchive -exportPath ./build -exportOptionsPlist ExportOptions.plist
   ```

3. **Upload to App Store Connect:**
   ```bash
   xcrun altool --upload-app -f ./build/Cleo.ipa -u <apple-id> -p <app-specific-password>
   ```

4. **Submit for review**

### Android

1. **Build release APK/AAB:**
   ```bash
   cd mobile/android
   ./gradlew bundleRelease
   ```

2. **Sign the build:**
   ```bash
   jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore release.keystore app-release.aab alias_name
   ```

3. **Upload to Google Play Console**

4. **Submit for review**

## Post-Deployment

### 1. Smoke Tests

```bash
# Test critical endpoints
curl https://api.cleo.ai/health
curl -X POST https://api.cleo.ai/api/v1/auth/login -d '{"email":"test@example.com","password":"test"}'
```

### 2. Monitor Metrics

- Response times
- Error rates
- Database performance
- Cache hit rates
- User activity

### 3. Rollback Plan

If issues arise:

```bash
# Rollback Kubernetes deployment
kubectl rollout undo deployment/user-service

# Restore database backup
psql -h <host> -U <user> -d cleo_prod < backup_2025-11-13.sql
```

## Scaling Strategy

### Horizontal Scaling

```bash
# Auto-scale based on CPU
kubectl autoscale deployment user-service --cpu-percent=70 --min=3 --max=10
```

### Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Sharding for very large datasets

## Security Hardening

- [ ] Enable HTTPS/TLS everywhere
- [ ] Configure WAF (Web Application Firewall)
- [ ] Set up DDoS protection
- [ ] Enable security headers (HSTS, CSP, etc.)
- [ ] Regular security scans
- [ ] Penetration testing
- [ ] Compliance audits (SOC 2, PCI DSS)

## Disaster Recovery

1. **Regular backups:** Automated daily backups
2. **Multi-region:** Deploy in multiple regions for failover
3. **Disaster recovery testing:** Quarterly DR drills
4. **Documentation:** Keep runbooks updated

---

For questions or issues during deployment, contact the DevOps team or consult the troubleshooting guide.
