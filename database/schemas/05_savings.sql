-- Savings goals table
CREATE TABLE IF NOT EXISTS savings_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Goal details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(100), -- emergency_fund, vacation, car, home, wedding, custom

    -- Financial details
    target_amount DECIMAL(12, 2) NOT NULL,
    current_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Timeline
    target_date DATE,
    started_at DATE NOT NULL DEFAULT CURRENT_DATE,
    completed_at DATE,

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,

    -- Autosave settings
    autosave_enabled BOOLEAN DEFAULT FALSE,
    autosave_amount DECIMAL(12, 2),
    autosave_frequency VARCHAR(50), -- daily, weekly, bi-weekly, monthly

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_savings_goals_user_id ON savings_goals(user_id);
CREATE INDEX idx_savings_goals_active ON savings_goals(is_active);
CREATE INDEX idx_savings_goals_completed ON savings_goals(is_completed);

CREATE TRIGGER update_savings_goals_updated_at BEFORE UPDATE ON savings_goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Savings transactions (deposits/withdrawals to goals)
CREATE TABLE IF NOT EXISTS savings_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_id UUID REFERENCES savings_goals(id) ON DELETE SET NULL,

    -- Transaction details
    amount DECIMAL(12, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- deposit, withdrawal
    method VARCHAR(100), -- autosave, manual, round_up, spare_change

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, completed, failed
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    description TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_transaction_type CHECK (transaction_type IN ('deposit', 'withdrawal')),
    CONSTRAINT check_status CHECK (status IN ('pending', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_savings_transactions_user_id ON savings_transactions(user_id);
CREATE INDEX idx_savings_transactions_goal_id ON savings_transactions(goal_id);
CREATE INDEX idx_savings_transactions_created_at ON savings_transactions(created_at);

CREATE TRIGGER update_savings_transactions_updated_at BEFORE UPDATE ON savings_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
