import SwiftUI

struct BudgetView: View {
    @StateObject private var viewModel = BudgetViewModel()
    @State private var showingAddBudget = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Total Budget Card
                    TotalBudgetCard(
                        totalBudget: viewModel.totalBudget,
                        totalSpent: viewModel.totalSpent
                    )
                    .padding(.horizontal)

                    // Budget List
                    if viewModel.budgets.isEmpty {
                        EmptyBudgetState()
                            .padding(.top, 50)
                    } else {
                        ForEach(viewModel.budgets) { budget in
                            BudgetCard(budget: budget)
                                .padding(.horizontal)
                        }
                    }
                }
                .padding(.vertical)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Budgets")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingAddBudget = true
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(Color(hex: "667EEA"))
                    }
                }
            }
            .sheet(isPresented: $showingAddBudget) {
                AddBudgetView(viewModel: viewModel)
            }
            .onAppear {
                viewModel.loadBudgets()
            }
        }
    }
}

struct TotalBudgetCard: View {
    let totalBudget: Double
    let totalSpent: Double

    var percentageUsed: Double {
        totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Monthly Budget")
                .font(.headline)

            HStack {
                VStack(alignment: .leading, spacing: 5) {
                    Text("$\(totalSpent, specifier: "%.0f") of $\(totalBudget, specifier: "%.0f")")
                        .font(.title2)
                        .fontWeight(.bold)

                    Text("\(Int(percentageUsed))% used")
                        .font(.subheadline)
                        .foregroundColor(percentageUsed > 90 ? .red : .secondary)
                }

                Spacer()

                CircularProgressView(progress: percentageUsed / 100, color: percentageUsed > 90 ? .red : Color(hex: "667EEA"))
                    .frame(width: 80, height: 80)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct BudgetCard: View {
    let budget: Budget

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(budget.category)
                    .font(.headline)
                Spacer()
                Text("$\(budget.spent, specifier: "%.0f") / $\(budget.amount, specifier: "%.0f")")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            ProgressView(value: budget.spent, total: budget.amount)
                .tint(budget.percentageUsed > 90 ? .red : Color(hex: "667EEA"))

            HStack {
                Text("Remaining: $\(budget.remaining, specifier: "%.0f")")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Text("\(Int(budget.percentageUsed))%")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(budget.percentageUsed > 90 ? .red : .primary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct EmptyBudgetState: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "chart.pie")
                .font(.system(size: 60))
                .foregroundColor(.gray)

            Text("No Budgets Yet")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Create your first budget to start\ntracking your spending")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
        }
    }
}

struct AddBudgetView: View {
    @ObservedObject var viewModel: BudgetViewModel
    @Environment(\.dismiss) var dismiss

    @State private var category = ""
    @State private var amount = ""
    @State private var selectedPeriod = "monthly"

    let categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities", "Healthcare", "Other"]
    let periods = ["weekly", "monthly", "yearly"]

    var body: some View {
        NavigationView {
            Form {
                Section("Category") {
                    Picker("Select Category", selection: $category) {
                        ForEach(categories, id: \.self) { cat in
                            Text(cat)
                        }
                    }
                }

                Section("Amount") {
                    TextField("Budget Amount", text: $amount)
                        .keyboardType(.decimalPad)
                }

                Section("Period") {
                    Picker("Period", selection: $selectedPeriod) {
                        ForEach(periods, id: \.self) { period in
                            Text(period.capitalized)
                        }
                    }
                    .pickerStyle(.segmented)
                }
            }
            .navigationTitle("Add Budget")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        if let amountValue = Double(amount), !category.isEmpty {
                            viewModel.createBudget(category: category, amount: amountValue, period: selectedPeriod)
                            dismiss()
                        }
                    }
                    .disabled(category.isEmpty || amount.isEmpty)
                }
            }
        }
    }
}

struct CircularProgressView: View {
    let progress: Double
    let color: Color

    var body: some View {
        ZStack {
            Circle()
                .stroke(color.opacity(0.2), lineWidth: 8)

            Circle()
                .trim(from: 0, to: progress)
                .stroke(color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                .rotationEffect(.degrees(-90))

            Text("\(Int(progress * 100))%")
                .font(.headline)
                .foregroundColor(color)
        }
    }
}

class BudgetViewModel: ObservableObject {
    @Published var budgets: [Budget] = []
    @Published var isLoading = false

    private let budgetService = BudgetService.shared
    private var cancellables = Set<AnyCancellable>()

    var totalBudget: Double {
        budgets.reduce(0) { $0 + $1.amount }
    }

    var totalSpent: Double {
        budgets.reduce(0) { $0 + $1.spent }
    }

    func loadBudgets() {
        isLoading = true

        budgetService.getBudgets()
            .sink(
                receiveCompletion: { [weak self] _ in
                    self?.isLoading = false
                },
                receiveValue: { [weak self] budgets in
                    self?.budgets = budgets
                }
            )
            .store(in: &cancellables)
    }

    func createBudget(category: String, amount: Double, period: String) {
        budgetService.createBudget(category: category, amount: amount, period: period)
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] budget in
                    self?.budgets.append(budget)
                }
            )
            .store(in: &cancellables)
    }
}

import Combine

#Preview {
    BudgetView()
}
