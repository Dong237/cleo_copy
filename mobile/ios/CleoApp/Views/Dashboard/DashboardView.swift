import SwiftUI

struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()
    @State private var showingAdvances = false
    @State private var showingCredit = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header Card
                    HeaderCard(
                        balance: viewModel.totalBalance,
                        income: viewModel.monthlyIncome,
                        spending: viewModel.monthlySpending
                    )
                    .padding(.horizontal)

                    // Quick Actions
                    QuickActionsView(
                        showingAdvances: $showingAdvances,
                        showingCredit: $showingCredit
                    )
                    .padding(.horizontal)

                    // Savings Progress
                    if !viewModel.savingsGoals.isEmpty {
                        SavingsProgressCard(goals: viewModel.savingsGoals)
                            .padding(.horizontal)
                    }

                    // Recent Transactions
                    if !viewModel.transactions.isEmpty {
                        RecentTransactionsCard(transactions: viewModel.transactions)
                            .padding(.horizontal)
                    }

                    // Budget Overview
                    if !viewModel.budgets.isEmpty {
                        BudgetOverviewCard(budgets: viewModel.budgets)
                            .padding(.horizontal)
                    }
                }
                .padding(.vertical)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Dashboard")
            .navigationBarTitleDisplayMode(.large)
            .onAppear {
                viewModel.loadDashboardData()
            }
            .refreshable {
                viewModel.loadDashboardData()
            }
        }
    }
}

struct HeaderCard: View {
    let balance: Double
    let income: Double
    let spending: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Total Balance")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.8))

            Text("$\(balance, specifier: "%.2f")")
                .font(.system(size: 42, weight: .bold, design: .rounded))
                .foregroundColor(.white)

            HStack(spacing: 30) {
                VStack(alignment: .leading) {
                    Text("Income")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                    Text("+$\(income, specifier: "%.0f")")
                        .font(.headline)
                        .foregroundColor(.green)
                }

                VStack(alignment: .leading) {
                    Text("Spending")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                    Text("-$\(spending, specifier: "%.0f")")
                        .font(.headline)
                        .foregroundColor(.red)
                }

                Spacer()
            }
        }
        .padding(25)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color(hex: "667EEA"), Color(hex: "764BA2")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(20)
        .shadow(radius: 10)
    }
}

struct QuickActionsView: View {
    @Binding var showingAdvances: Bool
    @Binding var showingCredit: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Quick Actions")
                .font(.headline)
                .padding(.horizontal)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 15) {
                    QuickActionButton(
                        icon: "bolt.fill",
                        title: "Get Advance",
                        color: .orange
                    ) {
                        showingAdvances = true
                    }

                    QuickActionButton(
                        icon: "creditcard.fill",
                        title: "Credit Builder",
                        color: .blue
                    ) {
                        showingCredit = true
                    }

                    QuickActionButton(
                        icon: "chart.line.uptrend.xyaxis",
                        title: "Analytics",
                        color: .green
                    ) {
                        // Navigate to analytics
                    }

                    QuickActionButton(
                        icon: "lightbulb.fill",
                        title: "Tips",
                        color: .purple
                    ) {
                        // Navigate to recommendations
                    }
                }
                .padding(.horizontal)
            }
        }
    }
}

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 10) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(color)
                    .cornerRadius(12)

                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
        }
        .frame(width: 90)
    }
}

struct SavingsProgressCard: View {
    let goals: [SavingsGoal]

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Savings Goals")
                .font(.headline)

            ForEach(goals.prefix(3)) { goal in
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text(goal.name)
                            .font(.subheadline)
                        Spacer()
                        Text("$\(goal.currentAmount, specifier: "%.0f") / $\(goal.targetAmount, specifier: "%.0f")")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    ProgressView(value: goal.currentAmount, total: goal.targetAmount)
                        .tint(Color(hex: "667EEA"))
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct RecentTransactionsCard: View {
    let transactions: [Transaction]

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Recent Transactions")
                .font(.headline)

            ForEach(transactions.prefix(5)) { transaction in
                HStack {
                    Image(systemName: iconForCategory(transaction.categoryPrimary))
                        .foregroundColor(Color(hex: "667EEA"))
                        .frame(width: 40, height: 40)
                        .background(Color(hex: "667EEA").opacity(0.1))
                        .cornerRadius(10)

                    VStack(alignment: .leading, spacing: 4) {
                        Text(transaction.merchantName ?? "Transaction")
                            .font(.subheadline)
                        Text(transaction.categoryPrimary ?? "Other")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Text("$\(abs(transaction.amount), specifier: "%.2f")")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(transaction.amount < 0 ? .red : .green)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }

    func iconForCategory(_ category: String?) -> String {
        guard let category = category?.lowercased() else { return "cart.fill" }

        if category.contains("food") || category.contains("restaurant") {
            return "fork.knife"
        } else if category.contains("transport") || category.contains("gas") {
            return "car.fill"
        } else if category.contains("shop") {
            return "cart.fill"
        } else if category.contains("entertainment") {
            return "tv.fill"
        } else {
            return "dollarsign.circle.fill"
        }
    }
}

struct BudgetOverviewCard: View {
    let budgets: [Budget]

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Budget Overview")
                .font(.headline)

            ForEach(budgets.prefix(3)) { budget in
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text(budget.category)
                            .font(.subheadline)
                        Spacer()
                        Text("\(Int(budget.percentageUsed))%")
                            .font(.caption)
                            .foregroundColor(budget.percentageUsed > 90 ? .red : .secondary)
                    }

                    ProgressView(value: budget.spent, total: budget.amount)
                        .tint(budget.percentageUsed > 90 ? .red : Color(hex: "667EEA"))
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

#Preview {
    DashboardView()
        .environmentObject(AuthViewModel())
}
