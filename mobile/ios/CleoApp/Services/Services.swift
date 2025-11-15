import Foundation
import Combine

class AuthService {
    static let shared = AuthService()
    private let client = APIClient.shared

    private init() {}

    // MARK: - Login
    func login(email: String, password: String) -> AnyPublisher<AuthResponse, Error> {
        let url = URL(string: "\(APIConfig.userServiceURL)\(APIConfig.authPath)/login")!
        let request = LoginRequest(email: email, password: password)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body, requiresAuth: false)
    }

    // MARK: - Register
    func register(email: String, password: String, fullName: String) -> AnyPublisher<AuthResponse, Error> {
        let url = URL(string: "\(APIConfig.userServiceURL)\(APIConfig.authPath)/register")!
        let request = RegisterRequest(email: email, password: password, fullName: fullName)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body, requiresAuth: false)
    }

    // MARK: - Get Current User
    func getCurrentUser() -> AnyPublisher<User, Error> {
        let url = URL(string: "\(APIConfig.userServiceURL)\(APIConfig.usersPath)/me")!
        return client.request(url: url, method: "GET", requiresAuth: true)
    }
}

class BankingService {
    static let shared = BankingService()
    private let client = APIClient.shared

    private init() {}

    func getTransactions(limit: Int = 20) -> AnyPublisher<[Transaction], Error> {
        let url = URL(string: "\(APIConfig.bankingServiceURL)\(APIConfig.transactionsPath)?limit=\(limit)")!

        return client.request(url: url, method: "GET")
            .map { (response: TransactionsResponse) in response.transactions }
            .eraseToAnyPublisher()
    }
}

struct TransactionsResponse: Codable {
    let transactions: [Transaction]
}

class BudgetService {
    static let shared = BudgetService()
    private let client = APIClient.shared

    private init() {}

    func getBudgets() -> AnyPublisher<[Budget], Error> {
        let url = URL(string: "\(APIConfig.budgetServiceURL)\(APIConfig.budgetsPath)")!

        return client.request(url: url, method: "GET")
            .map { (response: BudgetsResponse) in response.budgets }
            .eraseToAnyPublisher()
    }

    func createBudget(category: String, amount: Double, period: String) -> AnyPublisher<Budget, Error> {
        let url = URL(string: "\(APIConfig.budgetServiceURL)\(APIConfig.budgetsPath)")!
        let request = CreateBudgetRequest(category: category, amount: amount, period: period)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body)
    }
}

struct BudgetsResponse: Codable {
    let budgets: [Budget]
}

class ChatService {
    static let shared = ChatService()
    private let client = APIClient.shared

    private init() {}

    func sendMessage(_ message: String) -> AnyPublisher<SendMessageResponse, Error> {
        let url = URL(string: "\(APIConfig.chatServiceURL)\(APIConfig.chatPath)/message")!
        let request = SendMessageRequest(message: message)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body)
    }
}

class SavingsService {
    static let shared = SavingsService()
    private let client = APIClient.shared

    private init() {}

    func getGoals() -> AnyPublisher<[SavingsGoal], Error> {
        let url = URL(string: "\(APIConfig.savingsServiceURL)\(APIConfig.savingsPath)/goals")!

        return client.request(url: url, method: "GET")
            .map { (response: GoalsResponse) in response.goals }
            .eraseToAnyPublisher()
    }

    func createGoal(name: String, targetAmount: Double, deadline: String?) -> AnyPublisher<SavingsGoal, Error> {
        let url = URL(string: "\(APIConfig.savingsServiceURL)\(APIConfig.savingsPath)/goals")!
        let request = CreateSavingsGoalRequest(name: name, targetAmount: targetAmount, deadline: deadline)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body)
    }
}

struct GoalsResponse: Codable {
    let goals: [SavingsGoal]
}

class AdvanceService {
    static let shared = AdvanceService()
    private let client = APIClient.shared

    private init() {}

    func checkEligibility() -> AnyPublisher<AdvanceEligibility, Error> {
        let url = URL(string: "\(APIConfig.advanceServiceURL)\(APIConfig.advancesPath)/eligibility")!
        return client.request(url: url, method: "GET")
    }

    func requestAdvance(amount: Double) -> AnyPublisher<Advance, Error> {
        let url = URL(string: "\(APIConfig.advanceServiceURL)\(APIConfig.advancesPath)")!
        let request = RequestAdvanceRequest(amount: amount)

        guard let body = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.invalidResponse).eraseToAnyPublisher()
        }

        return client.request(url: url, method: "POST", body: body)
    }

    func getAdvances() -> AnyPublisher<[Advance], Error> {
        let url = URL(string: "\(APIConfig.advanceServiceURL)\(APIConfig.advancesPath)")!

        return client.request(url: url, method: "GET")
            .map { (response: AdvancesResponse) in response.advances }
            .eraseToAnyPublisher()
    }
}

struct AdvancesResponse: Codable {
    let advances: [Advance]
}

struct AdvanceEligibility: Codable {
    let eligible: Bool
    let maxAmount: Double
    let reason: String?
}

class CreditService {
    static let shared = CreditService()
    private let client = APIClient.shared

    private init() {}

    func getCreditScore() -> AnyPublisher<CreditScore, Error> {
        let url = URL(string: "\(APIConfig.creditServiceURL)\(APIConfig.creditPath)/score")!
        return client.request(url: url, method: "GET")
    }

    func enrollInCreditBuilder() -> AnyPublisher<CreditBuilderEnrollment, Error> {
        let url = URL(string: "\(APIConfig.creditServiceURL)\(APIConfig.creditPath)/builder/enroll")!
        return client.request(url: url, method: "POST", body: nil)
    }

    func getCreditActivity() -> AnyPublisher<[CreditActivity], Error> {
        let url = URL(string: "\(APIConfig.creditServiceURL)\(APIConfig.creditPath)/activity")!

        return client.request(url: url, method: "GET")
            .map { (response: CreditActivityResponse) in response.activities }
            .eraseToAnyPublisher()
    }
}

struct CreditActivityResponse: Codable {
    let activities: [CreditActivity]
}

struct CreditBuilderEnrollment: Codable {
    let success: Bool
    let message: String
    let monthlyContribution: Double?
}

struct CreditActivity: Codable, Identifiable {
    let id: String
    let date: String
    let description: String
    let impact: String
}

class AnalyticsService {
    static let shared = AnalyticsService()
    private let client = APIClient.shared

    private init() {}

    func getSpendingInsights(period: String = "month") -> AnyPublisher<SpendingInsights, Error> {
        let url = URL(string: "\(APIConfig.analyticsServiceURL)\(APIConfig.analyticsPath)/insights?period=\(period)")!
        return client.request(url: url, method: "GET")
    }
}

struct SpendingInsights: Codable {
    let totalSpending: Double
    let categoryBreakdown: [CategorySpending]
    let trend: String
}

struct CategorySpending: Codable, Identifiable {
    let id: String
    let category: String
    let amount: Double
    let percentage: Double
}

class RecommendationService {
    static let shared = RecommendationService()
    private let client = APIClient.shared

    private init() {}

    func getRecommendations() -> AnyPublisher<[Recommendation], Error> {
        let url = URL(string: "\(APIConfig.recommendationServiceURL)\(APIConfig.recommendationsPath)")!

        return client.request(url: url, method: "GET")
            .map { (response: RecommendationsResponse) in response.recommendations }
            .eraseToAnyPublisher()
    }
}

struct RecommendationsResponse: Codable {
    let recommendations: [Recommendation]
}

struct Recommendation: Codable, Identifiable {
    let id: String
    let type: String
    let title: String
    let description: String
    let potentialSavings: Double?
}
