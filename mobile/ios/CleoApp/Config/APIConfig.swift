import Foundation

struct APIConfig {
    // IMPORTANT: For iOS Simulator, use 127.0.0.1 instead of localhost
    // For physical device, use your Mac's IP address (e.g., 192.168.1.100)
    static let baseURL = "http://127.0.0.1"

    // Service ports
    static let userServicePort = 8001
    static let bankingServicePort = 8002
    static let budgetServicePort = 8003
    static let chatServicePort = 8004
    static let savingsServicePort = 8005
    static let notificationServicePort = 8006
    static let advanceServicePort = 8007
    static let creditServicePort = 8008
    static let analyticsServicePort = 8009
    static let recommendationServicePort = 8010

    // Full URLs
    static let userServiceURL = "\(baseURL):\(userServicePort)"
    static let bankingServiceURL = "\(baseURL):\(bankingServicePort)"
    static let budgetServiceURL = "\(baseURL):\(budgetServicePort)"
    static let chatServiceURL = "\(baseURL):\(chatServicePort)"
    static let savingsServiceURL = "\(baseURL):\(savingsServicePort)"
    static let notificationServiceURL = "\(baseURL):\(notificationServicePort)"
    static let advanceServiceURL = "\(baseURL):\(advanceServicePort)"
    static let creditServiceURL = "\(baseURL):\(creditServicePort)"
    static let analyticsServiceURL = "\(baseURL):\(analyticsServicePort)"
    static let recommendationServiceURL = "\(baseURL):\(recommendationServicePort)"

    // API paths
    static let authPath = "/api/v1/auth"
    static let usersPath = "/api/v1/users"
    static let transactionsPath = "/api/v1/transactions"
    static let budgetsPath = "/api/v1/budgets"
    static let chatPath = "/api/v1/chat"
    static let savingsPath = "/api/v1/savings"
    static let advancesPath = "/api/v1/advances"
    static let creditPath = "/api/v1/credit"
    static let analyticsPath = "/api/v1/analytics"
    static let recommendationsPath = "/api/v1/recommendations"
}
