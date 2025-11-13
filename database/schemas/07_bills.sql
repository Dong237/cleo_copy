-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Bill details
    name VARCHAR(255) NOT NULL,
    merchant_name VARCHAR(255),
    category VARCHAR(100),

    -- Amount
    amount DECIMAL(12, 2),
    is_variable BOOLEAN DEFAULT FALSE, -- true for utilities, false for fixed bills
    currency VARCHAR(3) DEFAULT 'USD',

    -- Recurrence
    frequency VARCHAR(50) NOT NULL, -- weekly, bi-weekly, monthly, quarterly, yearly
    next_due_date DATE NOT NULL,
    last_paid_date DATE,

    -- Detection
    auto_detected BOOLEAN DEFAULT FALSE,
    confirmed_by_user BOOLEAN DEFAULT FALSE,

    -- Reminders
    reminder_enabled BOOLEAN DEFAULT TRUE,
    remind_days_before INTEGER DEFAULT 3,

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_frequency CHECK (frequency IN ('weekly', 'bi-weekly', 'monthly', 'quarterly', 'yearly'))
);

CREATE INDEX idx_bills_user_id ON bills(user_id);
CREATE INDEX idx_bills_next_due_date ON bills(next_due_date);
CREATE INDEX idx_bills_active ON bills(is_active);

CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Bill payments history
CREATE TABLE IF NOT EXISTS bill_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,

    -- Payment details
    amount DECIMAL(12, 2) NOT NULL,
    paid_date DATE NOT NULL,
    due_date DATE NOT NULL,

    -- Status
    is_on_time BOOLEAN,
    is_late BOOLEAN,
    days_late INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bill_payments_bill_id ON bill_payments(bill_id);
CREATE INDEX idx_bill_payments_user_id ON bill_payments(user_id);
CREATE INDEX idx_bill_payments_paid_date ON bill_payments(paid_date);
