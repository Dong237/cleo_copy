import SwiftUI

struct SavingsView: View {
    @StateObject private var viewModel = SavingsViewModel()
    @State private var showingAddGoal = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Total Savings Card
                    TotalSavingsCard(totalSaved: viewModel.totalSaved, totalTarget: viewModel.totalTarget)
                        .padding(.horizontal)

                    // Goals List
                    if viewModel.goals.isEmpty {
                        EmptySavingsState()
                            .padding(.top, 50)
                    } else {
                        ForEach(viewModel.goals) { goal in
                            SavingsGoalCard(goal: goal)
                                .padding(.horizontal)
                        }
                    }
                }
                .padding(.vertical)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Savings")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingAddGoal = true
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(Color(hex: "667EEA"))
                    }
                }
            }
            .sheet(isPresented: $showingAddGoal) {
                AddSavingsGoalView(viewModel: viewModel)
            }
            .onAppear {
                viewModel.loadGoals()
            }
        }
    }
}

struct TotalSavingsCard: View {
    let totalSaved: Double
    let totalTarget: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Total Savings")
                .font(.headline)

            HStack {
                VStack(alignment: .leading, spacing: 5) {
                    Text("$\(totalSaved, specifier: "%.0f")")
                        .font(.system(size: 36, weight: .bold, design: .rounded))

                    Text("of $\(totalTarget, specifier: "%.0f") goal")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()
            }

            ProgressView(value: totalSaved, total: totalTarget)
                .tint(Color.green)
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color.green.opacity(0.1), Color.green.opacity(0.2)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(15)
    }
}

struct SavingsGoalCard: View {
    let goal: SavingsGoal

    var progress: Double {
        goal.targetAmount > 0 ? goal.currentAmount / goal.targetAmount : 0
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(goal.name)
                        .font(.headline)

                    if let deadline = goal.deadline {
                        Text("Target: \(formatDate(deadline))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                Text("\(Int(progress * 100))%")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(Color.green)
            }

            ProgressView(value: progress)
                .tint(Color.green)

            HStack {
                Text("$\(goal.currentAmount, specifier: "%.0f") saved")
                    .font(.subheadline)

                Spacer()

                Text("$\(goal.targetAmount - goal.currentAmount, specifier: "%.0f") to go")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }

    func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .medium
            return displayFormatter.string(from: date)
        }
        return dateString
    }
}

struct EmptySavingsState: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "banknote")
                .font(.system(size: 60))
                .foregroundColor(.gray)

            Text("No Savings Goals")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Create a goal to start\nsaving for something special")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
        }
    }
}

struct AddSavingsGoalView: View {
    @ObservedObject var viewModel: SavingsViewModel
    @Environment(\.dismiss) var dismiss

    @State private var name = ""
    @State private var targetAmount = ""
    @State private var deadline = Date().addingTimeInterval(86400 * 30) // 30 days from now

    var body: some View {
        NavigationView {
            Form {
                Section("Goal Name") {
                    TextField("e.g., Emergency Fund, Vacation", text: $name)
                }

                Section("Target Amount") {
                    TextField("Amount", text: $targetAmount)
                        .keyboardType(.decimalPad)
                }

                Section("Deadline") {
                    DatePicker("Target Date", selection: $deadline, displayedComponents: .date)
                }
            }
            .navigationTitle("New Savings Goal")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Create") {
                        if let amount = Double(targetAmount), !name.isEmpty {
                            let deadlineString = ISO8601DateFormatter().string(from: deadline)
                            viewModel.createGoal(name: name, targetAmount: amount, deadline: deadlineString)
                            dismiss()
                        }
                    }
                    .disabled(name.isEmpty || targetAmount.isEmpty)
                }
            }
        }
    }
}

class SavingsViewModel: ObservableObject {
    @Published var goals: [SavingsGoal] = []
    @Published var isLoading = false

    private let savingsService = SavingsService.shared
    private var cancellables = Set<AnyCancellable>()

    var totalSaved: Double {
        goals.reduce(0) { $0 + $1.currentAmount }
    }

    var totalTarget: Double {
        goals.reduce(0) { $0 + $1.targetAmount }
    }

    func loadGoals() {
        isLoading = true

        savingsService.getGoals()
            .sink(
                receiveCompletion: { [weak self] _ in
                    self?.isLoading = false
                },
                receiveValue: { [weak self] goals in
                    self?.goals = goals
                }
            )
            .store(in: &cancellables)
    }

    func createGoal(name: String, targetAmount: Double, deadline: String) {
        savingsService.createGoal(name: name, targetAmount: targetAmount, deadline: deadline)
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] goal in
                    self?.goals.append(goal)
                }
            )
            .store(in: &cancellables)
    }
}

import Combine

#Preview {
    SavingsView()
}
