-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Achievement definition
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    category VARCHAR(100), -- savings, budgeting, credit, engagement

    -- Requirements
    requirement_type VARCHAR(100), -- amount_saved, days_under_budget, credit_increase, etc.
    requirement_value DECIMAL(12, 2),

    -- Reward
    reward_points INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_achievements_code ON achievements(code);
CREATE INDEX idx_achievements_category ON achievements(category);


-- User achievements (earned)
CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,

    -- Status
    earned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    shared_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_earned_at ON user_achievements(earned_at);


-- Weekly quizzes
CREATE TABLE IF NOT EXISTS weekly_quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Quiz details
    week_start_date DATE NOT NULL UNIQUE,
    week_end_date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Prize
    prize_amount DECIMAL(12, 2),
    prize_currency VARCHAR(3) DEFAULT 'USD',

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_weekly_quizzes_week_start ON weekly_quizzes(week_start_date);
CREATE INDEX idx_weekly_quizzes_active ON weekly_quizzes(is_active);


-- Quiz questions
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES weekly_quizzes(id) ON DELETE CASCADE,

    -- Question details
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- multiple_choice, true_false, spend_estimate

    -- Options (for multiple choice)
    options JSONB,
    correct_answer TEXT,

    -- Order
    order_number INTEGER NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);


-- User quiz responses
CREATE TABLE IF NOT EXISTS quiz_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES weekly_quizzes(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,

    -- Response
    answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,

    -- Timestamps
    answered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, question_id)
);

CREATE INDEX idx_quiz_responses_user_id ON quiz_responses(user_id);
CREATE INDEX idx_quiz_responses_quiz_id ON quiz_responses(quiz_id);


-- Spending habits reviews (swipe feature)
CREATE TABLE IF NOT EXISTS spending_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,

    -- Review
    added_value BOOLEAN NOT NULL, -- true for thumbs up, false for thumbs down
    regret_reason VARCHAR(255),
    notes TEXT,

    -- Timestamps
    reviewed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, transaction_id)
);

CREATE INDEX idx_spending_reviews_user_id ON spending_reviews(user_id);
CREATE INDEX idx_spending_reviews_reviewed_at ON spending_reviews(reviewed_at);
CREATE INDEX idx_spending_reviews_added_value ON spending_reviews(added_value);
