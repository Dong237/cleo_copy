-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Budget details
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    period VARCHAR(50) NOT NULL DEFAULT 'monthly', -- weekly, bi-weekly, monthly

    -- Budget period
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Alerts
    alert_at_75_percent BOOLEAN DEFAULT TRUE,
    alert_at_90_percent BOOLEAN DEFAULT TRUE,
    alert_at_100_percent BOOLEAN DEFAULT TRUE,

    -- Rollover settings
    allow_rollover BOOLEAN DEFAULT FALSE,
    rollover_amount DECIMAL(12, 2) DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_budget_period CHECK (period IN ('weekly', 'bi-weekly', 'monthly', 'yearly'))
);

CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_category ON budgets(category);
CREATE INDEX idx_budgets_period ON budgets(start_date, end_date);
CREATE INDEX idx_budgets_active ON budgets(is_active);

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Budget alerts history
CREATE TABLE IF NOT EXISTS budget_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- 75_percent, 90_percent, 100_percent, exceeded
    amount_spent DECIMAL(12, 2) NOT NULL,
    budget_amount DECIMAL(12, 2) NOT NULL,
    percentage_used DECIMAL(5, 2) NOT NULL,

    -- Status
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_budget_alerts_budget_id ON budget_alerts(budget_id);
CREATE INDEX idx_budget_alerts_user_id ON budget_alerts(user_id);
CREATE INDEX idx_budget_alerts_sent_at ON budget_alerts(sent_at);
