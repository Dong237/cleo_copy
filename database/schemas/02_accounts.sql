-- Bank Accounts table (linked via Plaid)
CREATE TABLE IF NOT EXISTS bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Plaid information
    plaid_account_id VARCHAR(255) NOT NULL UNIQUE,
    plaid_item_id VARCHAR(255) NOT NULL,
    plaid_access_token TEXT NOT NULL,

    -- Account details
    account_name VARCHAR(255),
    account_type VARCHAR(50), -- checking, savings, credit
    account_subtype VARCHAR(50),
    institution_name VARCHAR(255),
    institution_id VARCHAR(255),

    -- Balance information
    current_balance DECIMAL(12, 2),
    available_balance DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_account_type CHECK (account_type IN ('checking', 'savings', 'credit', 'investment'))
);

CREATE INDEX idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE INDEX idx_bank_accounts_plaid_item ON bank_accounts(plaid_item_id);
CREATE INDEX idx_bank_accounts_active ON bank_accounts(is_active);

CREATE TRIGGER update_bank_accounts_updated_at BEFORE UPDATE ON bank_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
