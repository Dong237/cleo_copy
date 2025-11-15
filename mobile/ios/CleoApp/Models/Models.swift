import Foundation

// MARK: - User Models
struct User: Codable, Identifiable {
    let id: UUID
    let email: String
    let fullName: String?
    let personalityMode: String
    let subscriptionTier: String
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, email
        case fullName = "full_name"
        case personalityMode = "personality_mode"
        case subscriptionTier = "subscription_tier"
        case createdAt = "created_at"
    }
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let email: String
    let password: String
    let fullName: String

    enum CodingKeys: String, CodingKey {
        case email, password
        case fullName = "full_name"
    }
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let user: User

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case user
    }
}

// MARK: - Transaction Models
struct Transaction: Codable, Identifiable {
    let id: UUID
    let amount: Double
    let merchantName: String?
    let categoryPrimary: String?
    let date: String
    let pending: Bool

    enum CodingKeys: String, CodingKey {
        case id, amount, date, pending
        case merchantName = "merchant_name"
        case categoryPrimary = "category_primary"
    }
}

// MARK: - Budget Models
struct Budget: Codable, Identifiable {
    let id: UUID
    let category: String
    let amount: Double
    let period: String
    let spent: Double
    let remaining: Double
    let percentageUsed: Double

    enum CodingKeys: String, CodingKey {
        case id, category, amount, period, spent, remaining
        case percentageUsed = "percentage_used"
    }
}

struct CreateBudgetRequest: Codable {
    let category: String
    let amount: Double
    let period: String
}

// MARK: - Chat Models
struct ChatMessage: Codable, Identifiable {
    let id: UUID
    let role: String
    let content: String
    let timestamp: String
}

struct SendMessageRequest: Codable {
    let message: String
}

struct SendMessageResponse: Codable {
    let conversationId: UUID
    let message: ChatMessage

    enum CodingKeys: String, CodingKey {
        case conversationId = "conversation_id"
        case message
    }
}

// MARK: - Savings Models
struct SavingsGoal: Codable, Identifiable {
    let id: UUID
    let name: String
    let targetAmount: Double
    let currentAmount: Double
    let deadline: String?
    let status: String

    enum CodingKeys: String, CodingKey {
        case id, name, deadline, status
        case targetAmount = "target_amount"
        case currentAmount = "current_amount"
    }
}

struct CreateSavingsGoalRequest: Codable {
    let name: String
    let targetAmount: Double
    let deadline: String?

    enum CodingKeys: String, CodingKey {
        case name, deadline
        case targetAmount = "target_amount"
    }
}

// MARK: - Advance Models
struct Advance: Codable, Identifiable {
    let id: UUID
    let amount: Double
    let status: String
    let repaymentDueDate: String
    let totalAmount: Double

    enum CodingKeys: String, CodingKey {
        case id, amount, status
        case repaymentDueDate = "repayment_due_date"
        case totalAmount = "total_amount"
    }
}

struct EligibilityResponse: Codable {
    let isEligible: Bool
    let maxAdvanceAmount: Double
    let reason: String

    enum CodingKeys: String, CodingKey {
        case isEligible = "is_eligible"
        case maxAdvanceAmount = "max_advance_amount"
        case reason
    }
}

struct RequestAdvanceRequest: Codable {
    let amount: Double
}

// MARK: - Credit Models
struct CreditScore: Codable {
    let score: Int
    let scoreProvider: String
    let previousScore: Int?
    let scoreChange: Int?
    let checkedAt: String

    enum CodingKeys: String, CodingKey {
        case score
        case scoreProvider = "score_provider"
        case previousScore = "previous_score"
        case scoreChange = "score_change"
        case checkedAt = "checked_at"
    }
}

struct CreditCard: Codable, Identifiable {
    let id: UUID
    let status: String
    let creditLimit: Double
    let availableCredit: Double
    let currentBalance: Double
    let onTimePayments: Int

    enum CodingKeys: String, CodingKey {
        case id, status
        case creditLimit = "credit_limit"
        case availableCredit = "available_credit"
        case currentBalance = "current_balance"
        case onTimePayments = "on_time_payments"
    }
}

// MARK: - Analytics Models
struct FinancialHealthScore: Codable {
    let overallScore: Int
    let grade: String
    let message: String
    let trend: String

    enum CodingKeys: String, CodingKey {
        case overallScore = "overall_score"
        case grade, message, trend
    }
}

// MARK: - Dashboard Models
struct DashboardData: Codable {
    let totalBalance: Double
    let monthlyIncome: Double
    let monthlySpending: Double
    let savingsRate: Double
    let recentTransactions: [Transaction]

    enum CodingKeys: String, CodingKey {
        case totalBalance = "total_balance"
        case monthlyIncome = "monthly_income"
        case monthlySpending = "monthly_spending"
        case savingsRate = "savings_rate"
        case recentTransactions = "recent_transactions"
    }
}
