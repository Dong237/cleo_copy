-- Users table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,

    -- Profile information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_photo_url VARCHAR(500),

    -- Account status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    phone_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Preferences
    personality_mode VARCHAR(50) NOT NULL DEFAULT 'supportive',
    notification_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- Two-factor authentication
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(255),

    -- Subscription
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',
    subscription_started_at TIMESTAMP WITH TIME ZONE,
    subscription_ends_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    CONSTRAINT check_personality_mode CHECK (personality_mode IN ('funny', 'supportive', 'strict', 'roast')),
    CONSTRAINT check_subscription_tier CHECK (subscription_tier IN ('free', 'plus', 'builder'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
