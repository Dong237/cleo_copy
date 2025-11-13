# Contributing to Cleo Financial Assistant

Thank you for your interest in contributing to Cleo! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Collaborate constructively
- Focus on what's best for the community
- Show empathy towards others

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/cleo_copy.git
   cd cleo_copy
   ```

3. **Set up development environment:**
   ```bash
   ./scripts/setup.sh
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Backend Development

1. Make changes to the relevant service
2. Write tests for your changes
3. Run tests locally:
   ```bash
   cd backend/services/your-service
   pytest
   ```

4. Ensure code quality:
   ```bash
   black backend/
   isort backend/
   flake8 backend/
   ```

### Database Changes

1. Create SQL migration file in `database/schemas/`
2. Name it with incremental numbering: `12_your_feature.sql`
3. Test migration:
   ```bash
   ./scripts/run-migrations.sh
   ```

### Mobile Development

1. Follow platform-specific guidelines (see mobile/ios/README.md or mobile/android/README.md)
2. Ensure UI follows design system
3. Test on multiple screen sizes
4. Write unit and UI tests

## Pull Request Process

1. **Update Documentation:** Update README.md and relevant docs if needed
2. **Write Tests:** Ensure adequate test coverage (aim for 80%+)
3. **Pass CI Checks:** All GitHub Actions must pass
4. **Code Review:** Request review from at least 2 team members
5. **Squash Commits:** Keep history clean with meaningful commit messages

### PR Title Format

```
[SERVICE] Brief description

Examples:
[USER-SERVICE] Add email verification endpoint
[CHAT-SERVICE] Implement intent classification
[MOBILE-IOS] Create budget tracking UI
[DOCS] Update API documentation
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Backward compatible (or breaking change noted)
```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Use async/await for I/O operations
- Keep functions focused and small

**Example:**
```python
async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Retrieve user by email address.

    Args:
        email: User's email address
        db: Database session

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

### Swift (iOS)

- Follow Swift API Design Guidelines
- Use SwiftUI for UI
- Write unit tests with XCTest
- Document public APIs

### Kotlin (Android)

- Follow Kotlin coding conventions
- Use Jetpack Compose for UI
- Write unit tests with JUnit
- Document public APIs

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Mock external dependencies
- Aim for 80%+ coverage
- Use descriptive test names

**Example:**
```python
async def test_create_user_success(db_session):
    """Test successful user creation"""
    user_data = UserRegister(
        email="test@example.com",
        password="SecurePass123",
        first_name="Test"
    )

    user = await create_user(user_data, db_session)

    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert verify_password("SecurePass123", user.hashed_password)
```

### Integration Tests

- Test API endpoints end-to-end
- Use test database
- Clean up after tests

### E2E Tests

- Test critical user flows
- Automate with Playwright or Selenium
- Run in CI/CD pipeline

## Security

- **Never commit secrets:** Use environment variables
- **Sanitize inputs:** Validate and sanitize all user inputs
- **Use parameterized queries:** Prevent SQL injection
- **Encrypt sensitive data:** Use encryption for PII
- **Follow OWASP guidelines:** Regular security audits

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities. Email security@cleo.ai instead.

## Documentation

- Update API documentation for endpoint changes
- Add inline comments for complex logic
- Update README for new features
- Create ADRs (Architecture Decision Records) for significant decisions

## Commit Message Guidelines

Format: `type(scope): subject`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(user-service): add email verification
fix(chat-service): resolve intent classification bug
docs(api): update authentication endpoints
refactor(budget-service): simplify budget calculation logic
```

## Questions?

- Check existing issues and PRs
- Ask in team Slack channel
- Reach out to maintainers

Thank you for contributing! 🎉
