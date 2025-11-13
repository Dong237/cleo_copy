import Foundation
import Combine

class DashboardViewModel: ObservableObject {
    @Published var transactions: [Transaction] = []
    @Published var budgets: [Budget] = []
    @Published var savingsGoals: [SavingsGoal] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    // Mock dashboard data
    @Published var totalBalance: Double = 2750.00
    @Published var monthlyIncome: Double = 3500.00
    @Published var monthlySpending: Double = 2100.00
    @Published var savingsRate: Double = 18.5

    private var cancellables = Set<AnyCancellable>()

    func loadDashboardData() {
        isLoading = true
        errorMessage = nil

        // Load all data concurrently
        Publishers.Zip3(
            BankingService.shared.getTransactions(limit: 10),
            BudgetService.shared.getBudgets(),
            SavingsService.shared.getGoals()
        )
        .sink(
            receiveCompletion: { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                }
            },
            receiveValue: { [weak self] (transactions, budgets, goals) in
                self?.transactions = transactions
                self?.budgets = budgets
                self?.savingsGoals = goals
            }
        )
        .store(in: &cancellables)
    }

    var savingsAmount: Double {
        monthlyIncome - monthlySpending
    }
}
