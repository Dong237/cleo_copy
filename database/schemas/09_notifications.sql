-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Notification details
    type VARCHAR(100) NOT NULL, -- budget_alert, bill_reminder, insight, achievement, etc.
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,

    -- Delivery
    channel VARCHAR(50) NOT NULL, -- push, sms, email
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, urgent

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    data JSONB, -- Additional data for deep linking, etc.

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_channel CHECK (channel IN ('push', 'sms', 'email', 'in_app')),
    CONSTRAINT check_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT check_status CHECK (status IN ('pending', 'sent', 'failed', 'cancelled'))
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);


-- Notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,

    -- Channel preferences
    push_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    email_enabled BOOLEAN DEFAULT TRUE,

    -- Category preferences
    budget_alerts_enabled BOOLEAN DEFAULT TRUE,
    bill_reminders_enabled BOOLEAN DEFAULT TRUE,
    insights_enabled BOOLEAN DEFAULT TRUE,
    achievements_enabled BOOLEAN DEFAULT TRUE,
    marketing_enabled BOOLEAN DEFAULT FALSE,

    -- Quiet hours
    quiet_hours_enabled BOOLEAN DEFAULT FALSE,
    quiet_hours_start TIME,
    quiet_hours_end TIME,

    -- Frequency
    digest_frequency VARCHAR(50) DEFAULT 'daily', -- real_time, daily, weekly

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT check_digest_frequency CHECK (digest_frequency IN ('real_time', 'daily', 'weekly', 'never'))
);

CREATE INDEX idx_notification_preferences_user_id ON notification_preferences(user_id);

CREATE TRIGGER update_notification_preferences_updated_at BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
