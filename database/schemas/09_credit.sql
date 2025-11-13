-- Credit Schema
-- Credit score monitoring, credit builder, and coaching

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Credit scores table
CREATE TABLE IF NOT EXISTS credit_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Credit score data
    score INTEGER NOT NULL CHECK (score >= 300 AND score <= 850),
    score_provider VARCHAR(100) DEFAULT 'TransUnion',
    score_model VARCHAR(100) DEFAULT 'VantageScore 3.0',

    -- Score factors
    factors JSONB,
    credit_utilization NUMERIC(5, 2),
    payment_history_score INTEGER CHECK (payment_history_score >= 0 AND payment_history_score <= 100),
    credit_age_months INTEGER,
    total_accounts INTEGER,
    hard_inquiries INTEGER,

    -- Change tracking
    previous_score INTEGER,
    score_change INTEGER,

    -- Monitoring
    alert_threshold INTEGER DEFAULT 10,
    monitoring_enabled BOOLEAN DEFAULT TRUE,

    checked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit builder cards table
CREATE TABLE IF NOT EXISTS credit_builder_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,

    -- Card details
    card_number_last4 VARCHAR(4),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'closed', 'suspended')),
    credit_limit NUMERIC(12, 2) DEFAULT 500.00,
    available_credit NUMERIC(12, 2) DEFAULT 500.00,
    current_balance NUMERIC(12, 2) DEFAULT 0.00,

    -- Security deposit
    security_deposit NUMERIC(12, 2),
    deposit_status VARCHAR(50) CHECK (deposit_status IN ('pending', 'held', 'returned')),

    -- Dates
    applied_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    activated_at TIMESTAMP,
    closed_at TIMESTAMP,

    -- Settings
    autopay_enabled BOOLEAN DEFAULT TRUE,
    statement_day INTEGER DEFAULT 1 CHECK (statement_day >= 1 AND statement_day <= 28),
    due_day INTEGER DEFAULT 15 CHECK (due_day >= 1 AND due_day <= 28),

    -- Performance tracking
    on_time_payments INTEGER DEFAULT 0,
    late_payments INTEGER DEFAULT 0,
    months_active INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Credit builder transactions table
CREATE TABLE IF NOT EXISTS credit_builder_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID NOT NULL REFERENCES credit_builder_cards(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Transaction details
    amount NUMERIC(12, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('purchase', 'payment', 'fee', 'interest')),
    merchant_name VARCHAR(255),
    category VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'posted' CHECK (status IN ('pending', 'posted', 'reversed')),

    -- Dates
    transaction_date DATE NOT NULL,
    posted_date DATE,

    -- Reference
    description TEXT,
    external_transaction_id VARCHAR(255),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit builder payments table
CREATE TABLE IF NOT EXISTS credit_builder_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID NOT NULL REFERENCES credit_builder_cards(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Payment details
    amount NUMERIC(12, 2) NOT NULL,
    payment_type VARCHAR(50) CHECK (payment_type IN ('minimum', 'full', 'custom')),
    payment_method VARCHAR(100),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'processing', 'completed', 'failed')),
    is_autopay BOOLEAN DEFAULT FALSE,

    -- Dates
    due_date DATE NOT NULL,
    scheduled_date DATE,
    completed_date DATE,

    -- On-time tracking
    is_on_time BOOLEAN,
    days_late INTEGER DEFAULT 0,

    -- Failure handling
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Credit coaching sessions table
CREATE TABLE IF NOT EXISTS credit_coaching_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session details
    topic VARCHAR(255) NOT NULL,
    content TEXT,
    recommendations JSONB,

    -- Progress tracking
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,

    -- Impact
    estimated_score_impact INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit alerts table
CREATE TABLE IF NOT EXISTS credit_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Alert details
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Alert data
    alert_data JSONB,

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    is_dismissed BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_credit_scores_user_id ON credit_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_scores_checked_at ON credit_scores(checked_at DESC);

CREATE INDEX IF NOT EXISTS idx_credit_builder_cards_user_id ON credit_builder_cards(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_builder_cards_status ON credit_builder_cards(status);

CREATE INDEX IF NOT EXISTS idx_credit_builder_transactions_card_id ON credit_builder_transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_credit_builder_transactions_user_id ON credit_builder_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_builder_transactions_date ON credit_builder_transactions(transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_credit_builder_payments_card_id ON credit_builder_payments(card_id);
CREATE INDEX IF NOT EXISTS idx_credit_builder_payments_user_id ON credit_builder_payments(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_builder_payments_status ON credit_builder_payments(status);

CREATE INDEX IF NOT EXISTS idx_credit_coaching_sessions_user_id ON credit_coaching_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_coaching_sessions_completed ON credit_coaching_sessions(completed);

CREATE INDEX IF NOT EXISTS idx_credit_alerts_user_id ON credit_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_alerts_is_read ON credit_alerts(is_read);
CREATE INDEX IF NOT EXISTS idx_credit_alerts_created_at ON credit_alerts(created_at DESC);

-- Comments
COMMENT ON TABLE credit_scores IS 'Credit score history and monitoring';
COMMENT ON TABLE credit_builder_cards IS 'Credit builder card accounts';
COMMENT ON TABLE credit_builder_transactions IS 'Transactions on credit builder cards';
COMMENT ON TABLE credit_builder_payments IS 'Payment history for credit builder cards';
COMMENT ON TABLE credit_coaching_sessions IS 'Credit coaching and education sessions';
COMMENT ON TABLE credit_alerts IS 'Credit monitoring alerts';
