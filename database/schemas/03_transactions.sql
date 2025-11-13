-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES bank_accounts(id) ON DELETE CASCADE,

    -- Plaid transaction data
    plaid_transaction_id VARCHAR(255) UNIQUE,

    -- Transaction details
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    date DATE NOT NULL,
    authorized_date DATE,

    -- Merchant information
    merchant_name VARCHAR(255),
    merchant_logo_url VARCHAR(500),

    -- Categorization
    category_primary VARCHAR(100),
    category_detailed VARCHAR(100),

    -- Transaction metadata
    description TEXT,
    pending BOOLEAN DEFAULT FALSE,
    transaction_type VARCHAR(50), -- debit, credit

    -- User customization
    user_category VARCHAR(100), -- User can override auto-categorization
    user_notes TEXT,
    excluded_from_budget BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_primary);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_name);
CREATE INDEX idx_transactions_user_category ON transactions(user_category);

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
