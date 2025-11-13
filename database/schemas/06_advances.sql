-- Cash advances table
CREATE TABLE IF NOT EXISTS cash_advances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Advance details
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Repayment
    repayment_date DATE NOT NULL,
    repaid_at TIMESTAMP WITH TIME ZONE,
    repayment_amount DECIMAL(12, 2),

    -- Fees
    instant_fee DECIMAL(12, 2) DEFAULT 0,
    late_fee DECIMAL(12, 2) DEFAULT 0,
    tip_amount DECIMAL(12, 2) DEFAULT 0,

    -- Delivery
    delivery_method VARCHAR(50) NOT NULL, -- standard, instant
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    delivered_at TIMESTAMP WITH TIME ZONE,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, approved, disbursed, repaid, failed, cancelled

    -- Risk assessment
    eligibility_score DECIMAL(5, 2),
    risk_level VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_delivery_method CHECK (delivery_method IN ('standard', 'instant')),
    CONSTRAINT check_status CHECK (status IN ('pending', 'approved', 'disbursed', 'repaid', 'failed', 'cancelled', 'late'))
);

CREATE INDEX idx_cash_advances_user_id ON cash_advances(user_id);
CREATE INDEX idx_cash_advances_status ON cash_advances(status);
CREATE INDEX idx_cash_advances_repayment_date ON cash_advances(repayment_date);
CREATE INDEX idx_cash_advances_created_at ON cash_advances(created_at);

CREATE TRIGGER update_cash_advances_updated_at BEFORE UPDATE ON cash_advances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Advance eligibility history
CREATE TABLE IF NOT EXISTS advance_eligibility (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Eligibility details
    is_eligible BOOLEAN NOT NULL,
    max_amount DECIMAL(12, 2),
    reason TEXT,

    -- Scoring factors
    income_score DECIMAL(5, 2),
    banking_history_score DECIMAL(5, 2),
    repayment_history_score DECIMAL(5, 2),
    overall_score DECIMAL(5, 2),

    -- Timestamps
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_advance_eligibility_user_id ON advance_eligibility(user_id);
CREATE INDEX idx_advance_eligibility_checked_at ON advance_eligibility(checked_at);
