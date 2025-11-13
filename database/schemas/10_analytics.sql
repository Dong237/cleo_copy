-- Analytics Schema
-- Data aggregation, user behavior tracking, and business intelligence

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User analytics table
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Engagement metrics
    session_count INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    average_session_duration_seconds INTEGER DEFAULT 0,
    last_active_at TIMESTAMP,

    -- Feature usage
    chat_messages_sent INTEGER DEFAULT 0,
    budgets_created INTEGER DEFAULT 0,
    savings_goals_created INTEGER DEFAULT 0,
    advances_requested INTEGER DEFAULT 0,

    -- Financial health indicators
    total_saved NUMERIC(12, 2) DEFAULT 0.00,
    total_advanced NUMERIC(12, 2) DEFAULT 0.00,
    credit_score_improvement INTEGER DEFAULT 0,

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Financial metrics table
CREATE TABLE IF NOT EXISTS financial_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Income metrics
    total_income NUMERIC(12, 2) DEFAULT 0.00,
    average_monthly_income NUMERIC(12, 2) DEFAULT 0.00,

    -- Spending metrics
    total_spending NUMERIC(12, 2) DEFAULT 0.00,
    average_monthly_spending NUMERIC(12, 2) DEFAULT 0.00,

    -- Category breakdown
    spending_by_category JSONB,

    -- Savings metrics
    total_saved NUMERIC(12, 2) DEFAULT 0.00,
    savings_rate NUMERIC(5, 2),

    -- Budget adherence
    budget_adherence_rate NUMERIC(5, 2),
    over_budget_categories JSONB,

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Business metrics table
CREATE TABLE IF NOT EXISTS business_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User metrics
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    churned_users INTEGER DEFAULT 0,

    -- Subscription metrics
    free_tier_users INTEGER DEFAULT 0,
    plus_tier_users INTEGER DEFAULT 0,
    builder_tier_users INTEGER DEFAULT 0,

    -- Revenue metrics
    mrr NUMERIC(12, 2) DEFAULT 0.00,
    arr NUMERIC(12, 2) DEFAULT 0.00,

    -- Engagement metrics
    average_sessions_per_user NUMERIC(5, 2),
    average_session_duration INTEGER,

    -- Financial product usage
    total_advances_issued INTEGER DEFAULT 0,
    total_advance_amount NUMERIC(12, 2) DEFAULT 0.00,
    credit_builder_cards_active INTEGER DEFAULT 0,

    -- Time period
    period_date DATE NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Event logs table
CREATE TABLE IF NOT EXISTS event_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(100) NOT NULL,
    event_name VARCHAR(255) NOT NULL,

    -- Event data
    event_data JSONB,

    -- Context
    service_name VARCHAR(100),
    session_id VARCHAR(255),

    -- Timestamp
    event_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analytics_period ON user_analytics(period_start, period_end);

CREATE INDEX IF NOT EXISTS idx_financial_metrics_user_id ON financial_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_period ON financial_metrics(period_start, period_end);

CREATE INDEX IF NOT EXISTS idx_business_metrics_date ON business_metrics(period_date DESC);

CREATE INDEX IF NOT EXISTS idx_event_logs_user_id ON event_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_event_logs_type ON event_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_event_logs_category ON event_logs(event_category);
CREATE INDEX IF NOT EXISTS idx_event_logs_timestamp ON event_logs(event_timestamp DESC);

-- Comments
COMMENT ON TABLE user_analytics IS 'User behavior and engagement analytics';
COMMENT ON TABLE financial_metrics IS 'Aggregated financial metrics per user';
COMMENT ON TABLE business_metrics IS 'Business-level aggregated metrics';
COMMENT ON TABLE event_logs IS 'Event tracking for user actions';
