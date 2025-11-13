-- Credit builder cards table
CREATE TABLE IF NOT EXISTS credit_builder_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Card details
    card_number_last_4 VARCHAR(4),
    card_holder_name VARCHAR(255),
    expiry_month INTEGER,
    expiry_year INTEGER,

    -- Card tokens (encrypted)
    card_token VARCHAR(255) UNIQUE,
    virtual_card_number VARCHAR(255), -- Encrypted

    -- Security deposit
    deposit_amount DECIMAL(12, 2) NOT NULL,
    credit_limit DECIMAL(12, 2) NOT NULL,
    available_credit DECIMAL(12, 2) NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, active, suspended, closed

    -- Activation
    activated_at TIMESTAMP WITH TIME ZONE,
    physical_card_requested BOOLEAN DEFAULT FALSE,
    physical_card_shipped_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_status CHECK (status IN ('pending', 'active', 'suspended', 'closed'))
);

CREATE INDEX idx_credit_builder_cards_user_id ON credit_builder_cards(user_id);
CREATE INDEX idx_credit_builder_cards_status ON credit_builder_cards(status);

CREATE TRIGGER update_credit_builder_cards_updated_at BEFORE UPDATE ON credit_builder_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Credit score tracking
CREATE TABLE IF NOT EXISTS credit_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Score details
    score INTEGER NOT NULL,
    score_date DATE NOT NULL,
    bureau VARCHAR(50), -- experian, equifax, transunion
    score_model VARCHAR(50) DEFAULT 'VantageScore 3.0',

    -- Score factors
    payment_history_score INTEGER,
    credit_utilization_score INTEGER,
    age_of_credit_score INTEGER,
    credit_mix_score INTEGER,
    new_credit_score INTEGER,

    -- Additional data
    factors_affecting JSONB,
    recommendations JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_bureau CHECK (bureau IN ('experian', 'equifax', 'transunion', 'vantage'))
);

CREATE INDEX idx_credit_scores_user_id ON credit_scores(user_id);
CREATE INDEX idx_credit_scores_score_date ON credit_scores(score_date);
CREATE INDEX idx_credit_scores_bureau ON credit_scores(bureau);


-- Credit report monitoring
CREATE TABLE IF NOT EXISTS credit_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Alert details
    alert_type VARCHAR(100) NOT NULL, -- score_change, new_account, inquiry, etc.
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) DEFAULT 'info', -- info, warning, critical

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_severity CHECK (severity IN ('info', 'warning', 'critical'))
);

CREATE INDEX idx_credit_alerts_user_id ON credit_alerts(user_id);
CREATE INDEX idx_credit_alerts_created_at ON credit_alerts(created_at);
CREATE INDEX idx_credit_alerts_is_read ON credit_alerts(is_read);
