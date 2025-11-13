-- Advances Schema
-- Cash advance records and repayment management

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Advances table
CREATE TABLE IF NOT EXISTS advances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Advance details
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 20 AND amount <= 250),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'disbursed', 'repaid', 'failed', 'cancelled')),

    -- Dates
    requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP,
    disbursed_at TIMESTAMP,
    repayment_due_date TIMESTAMP NOT NULL,
    repaid_at TIMESTAMP,

    -- Fees
    instant_delivery_fee NUMERIC(12, 2) DEFAULT 0.00,
    tip_amount NUMERIC(12, 2) DEFAULT 0.00,
    total_amount NUMERIC(12, 2) NOT NULL,

    -- Underwriting
    risk_score NUMERIC(5, 2) CHECK (risk_score >= 0 AND risk_score <= 100),
    underwriting_notes TEXT,

    -- Repayment tracking
    repayment_status VARCHAR(50) DEFAULT 'pending' CHECK (repayment_status IN ('pending', 'scheduled', 'completed', 'failed')),
    repayment_attempts INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Eligibility checks table
CREATE TABLE IF NOT EXISTS eligibility_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Eligibility results
    is_eligible BOOLEAN NOT NULL,
    max_advance_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    reason TEXT,

    -- Factors considered
    has_regular_income BOOLEAN,
    income_history_days INTEGER,
    has_recent_overdrafts BOOLEAN,
    average_balance NUMERIC(12, 2),
    previous_advance_count INTEGER DEFAULT 0,
    previous_repayment_success_rate NUMERIC(5, 2),

    checked_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Repayments table
CREATE TABLE IF NOT EXISTS repayments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    advance_id UUID NOT NULL REFERENCES advances(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Repayment details
    amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'processing', 'completed', 'failed')),

    -- Dates
    scheduled_date TIMESTAMP NOT NULL,
    attempted_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Payment method
    payment_method VARCHAR(100),
    transaction_id VARCHAR(255),

    -- Failure handling
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_advances_user_id ON advances(user_id);
CREATE INDEX IF NOT EXISTS idx_advances_status ON advances(status);
CREATE INDEX IF NOT EXISTS idx_advances_repayment_status ON advances(repayment_status);
CREATE INDEX IF NOT EXISTS idx_advances_due_date ON advances(repayment_due_date);

CREATE INDEX IF NOT EXISTS idx_eligibility_user_id ON eligibility_checks(user_id);
CREATE INDEX IF NOT EXISTS idx_eligibility_checked_at ON eligibility_checks(checked_at DESC);

CREATE INDEX IF NOT EXISTS idx_repayments_advance_id ON repayments(advance_id);
CREATE INDEX IF NOT EXISTS idx_repayments_user_id ON repayments(user_id);
CREATE INDEX IF NOT EXISTS idx_repayments_status ON repayments(status);
CREATE INDEX IF NOT EXISTS idx_repayments_scheduled_date ON repayments(scheduled_date);

-- Comments
COMMENT ON TABLE advances IS 'Cash advance records';
COMMENT ON TABLE eligibility_checks IS 'User eligibility check history';
COMMENT ON TABLE repayments IS 'Repayment transaction records';
