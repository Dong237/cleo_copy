-- Recommendations Schema
-- ML-powered recommendations and insights

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Recommendation details
    recommendation_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Priority and impact
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    estimated_savings NUMERIC(12, 2),
    confidence_score NUMERIC(5, 2) CHECK (confidence_score >= 0 AND confidence_score <= 100),

    -- Action items
    action_items JSONB,

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'dismissed', 'completed')),
    viewed BOOLEAN DEFAULT FALSE,
    acted_on BOOLEAN DEFAULT FALSE,

    -- Metadata
    recommendation_data JSONB,
    model_version VARCHAR(50),

    -- Dates
    valid_until TIMESTAMP,
    viewed_at TIMESTAMP,
    acted_on_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Spending patterns table
CREATE TABLE IF NOT EXISTS spending_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Pattern details
    pattern_type VARCHAR(100) NOT NULL CHECK (pattern_type IN ('recurring', 'spike', 'trend')),
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,

    -- Pattern characteristics
    frequency VARCHAR(50),
    average_amount NUMERIC(12, 2),
    trend VARCHAR(50),

    -- Detection
    confidence NUMERIC(5, 2) CHECK (confidence >= 0 AND confidence <= 100),
    first_detected TIMESTAMP DEFAULT NOW(),
    last_occurrence TIMESTAMP,

    -- Pattern data
    pattern_data JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Savings opportunities table
CREATE TABLE IF NOT EXISTS savings_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Opportunity details
    opportunity_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Savings potential
    estimated_monthly_savings NUMERIC(12, 2) NOT NULL,
    estimated_annual_savings NUMERIC(12, 2) NOT NULL,
    confidence NUMERIC(5, 2) CHECK (confidence >= 0 AND confidence <= 100),

    -- Difficulty
    difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),

    -- Status
    status VARCHAR(50) DEFAULT 'identified' CHECK (status IN ('identified', 'presented', 'acted_on')),
    presented_at TIMESTAMP,
    acted_on_at TIMESTAMP,

    -- Opportunity data
    opportunity_data JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Insight feedback table
CREATE TABLE IF NOT EXISTS insight_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_id UUID,

    -- Feedback
    helpful BOOLEAN,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,

    -- Action taken
    action_taken BOOLEAN DEFAULT FALSE,
    action_description TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_created ON recommendations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_spending_patterns_user_id ON spending_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_spending_patterns_type ON spending_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_spending_patterns_confidence ON spending_patterns(confidence DESC);

CREATE INDEX IF NOT EXISTS idx_savings_opportunities_user_id ON savings_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_savings_opportunities_status ON savings_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_savings_opportunities_savings ON savings_opportunities(estimated_annual_savings DESC);

CREATE INDEX IF NOT EXISTS idx_insight_feedback_user_id ON insight_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_insight_feedback_recommendation_id ON insight_feedback(recommendation_id);

-- Comments
COMMENT ON TABLE recommendations IS 'Personalized financial recommendations';
COMMENT ON TABLE spending_patterns IS 'Identified spending patterns and trends';
COMMENT ON TABLE savings_opportunities IS 'Identified savings opportunities';
COMMENT ON TABLE insight_feedback IS 'User feedback on recommendations and insights';
