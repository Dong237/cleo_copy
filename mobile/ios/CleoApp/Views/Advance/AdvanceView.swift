import SwiftUI

struct AdvanceView: View {
    @StateObject private var viewModel = AdvanceViewModel()
    @State private var showingRequestAdvance = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Advance Limit Card
                    AdvanceLimitCard(
                        availableLimit: viewModel.availableLimit,
                        totalLimit: viewModel.totalLimit,
                        outstandingBalance: viewModel.outstandingBalance
                    )
                    .padding(.horizontal)

                    // How It Works Section
                    HowItWorksSection()
                        .padding(.horizontal)

                    // Request Advance Button
                    Button(action: {
                        showingRequestAdvance = true
                    }) {
                        HStack {
                            Image(systemName: "bolt.fill")
                            Text("Request Advance")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(hex: "667EEA"))
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal)
                    .disabled(viewModel.availableLimit <= 0)

                    // Recent Advances List
                    if !viewModel.advances.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Recent Advances")
                                .font(.title3)
                                .fontWeight(.bold)
                                .padding(.horizontal)

                            ForEach(viewModel.advances) { advance in
                                AdvanceCard(advance: advance)
                                    .padding(.horizontal)
                            }
                        }
                    } else {
                        EmptyAdvanceState()
                            .padding(.top, 30)
                    }
                }
                .padding(.vertical)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Cash Advance")
            .sheet(isPresented: $showingRequestAdvance) {
                RequestAdvanceView(viewModel: viewModel)
            }
            .onAppear {
                viewModel.loadAdvances()
            }
        }
    }
}

struct AdvanceLimitCard: View {
    let availableLimit: Double
    let totalLimit: Double
    let outstandingBalance: Double

    var percentageUsed: Double {
        totalLimit > 0 ? ((totalLimit - availableLimit) / totalLimit) : 0
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Your Advance Limit")
                .font(.headline)

            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    Text("$\(availableLimit, specifier: "%.0f")")
                        .font(.system(size: 42, weight: .bold, design: .rounded))
                        .foregroundColor(.white)

                    Text("Available of $\(totalLimit, specifier: "%.0f")")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))

                    if outstandingBalance > 0 {
                        Text("Outstanding: $\(outstandingBalance, specifier: "%.2f")")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                    }
                }

                Spacer()

                Image(systemName: "bolt.circle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.white.opacity(0.8))
            }

            ProgressView(value: percentageUsed)
                .tint(.white)
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color(hex: "667EEA"), Color(hex: "764BA2")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(15)
        .shadow(radius: 3)
    }
}

struct HowItWorksSection: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("How It Works")
                .font(.headline)

            VStack(alignment: .leading, spacing: 12) {
                HowItWorksStep(
                    icon: "1.circle.fill",
                    title: "Request",
                    description: "Get up to $250 instantly"
                )

                HowItWorksStep(
                    icon: "2.circle.fill",
                    title: "Receive",
                    description: "Money sent to your account"
                )

                HowItWorksStep(
                    icon: "3.circle.fill",
                    title: "Repay",
                    description: "Auto-deducted on next payday"
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct HowItWorksStep: View {
    let icon: String
    let title: String
    let description: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(Color(hex: "667EEA"))
                .frame(width: 30)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)

                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct AdvanceCard: View {
    let advance: Advance

    var statusColor: Color {
        switch advance.status {
        case "approved", "disbursed":
            return .green
        case "pending":
            return .orange
        case "repaid":
            return .blue
        default:
            return .red
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("$\(advance.amount, specifier: "%.2f")")
                        .font(.title3)
                        .fontWeight(.bold)

                    if let date = advance.requestDate {
                        Text(formatDate(date))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                Text(advance.status.capitalized)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(statusColor.opacity(0.2))
                    .foregroundColor(statusColor)
                    .cornerRadius(8)
            }

            if let repaymentDate = advance.repaymentDate {
                HStack {
                    Image(systemName: "calendar")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Text("Repayment: \(formatDate(repaymentDate))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            if let fee = advance.fee, fee > 0 {
                HStack {
                    Text("Fee: $\(fee, specifier: "%.2f")")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Spacer()

                    Text("Total: $\(advance.amount + fee, specifier: "%.2f")")
                        .font(.caption)
                        .fontWeight(.semibold)
                }
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

struct EmptyAdvanceState: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "bolt.slash")
                .font(.system(size: 60))
                .foregroundColor(.gray)

            Text("No Advances Yet")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Request your first advance\nto get started")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
        }
    }
}

struct RequestAdvanceView: View {
    @ObservedObject var viewModel: AdvanceViewModel
    @Environment(\.dismiss) var dismiss

    @State private var amount = ""
    @State private var reason = "Emergency expense"

    let reasons = ["Emergency expense", "Bill payment", "Unexpected cost", "Bridge to payday", "Other"]

    var body: some View {
        NavigationView {
            Form {
                Section("Amount") {
                    HStack {
                        Text("$")
                            .foregroundColor(.secondary)
                        TextField("0.00", text: $amount)
                            .keyboardType(.decimalPad)
                    }

                    Text("Available: $\(viewModel.availableLimit, specifier: "%.0f")")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section("Reason") {
                    Picker("Select Reason", selection: $reason) {
                        ForEach(reasons, id: \.self) { reason in
                            Text(reason)
                        }
                    }
                }

                Section("Repayment") {
                    HStack {
                        Text("Repayment Date")
                        Spacer()
                        Text("Next Payday")
                            .foregroundColor(.secondary)
                    }

                    if let amountValue = Double(amount), amountValue > 0 {
                        HStack {
                            Text("Fee (3%)")
                            Spacer()
                            Text("$\(amountValue * 0.03, specifier: "%.2f")")
                                .foregroundColor(.secondary)
                        }

                        HStack {
                            Text("Total Repayment")
                            Spacer()
                            Text("$\(amountValue * 1.03, specifier: "%.2f")")
                                .fontWeight(.semibold)
                        }
                    }
                }

                Section {
                    Text("Money will be deposited to your linked bank account within 1 business day. Repayment will be automatically deducted on your next payday.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Request Advance")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Request") {
                        if let amountValue = Double(amount) {
                            viewModel.requestAdvance(amount: amountValue, reason: reason)
                            dismiss()
                        }
                    }
                    .disabled(amount.isEmpty || Double(amount) ?? 0 <= 0)
                }
            }
        }
    }
}

class AdvanceViewModel: ObservableObject {
    @Published var advances: [Advance] = []
    @Published var availableLimit: Double = 250.0
    @Published var totalLimit: Double = 250.0
    @Published var outstandingBalance: Double = 0.0
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    func loadAdvances() {
        isLoading = true

        // Mock data for demo
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.advances = [
                Advance(
                    id: UUID(),
                    userId: UUID(),
                    amount: 50.0,
                    fee: 1.5,
                    status: "repaid",
                    requestDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 7)),
                    repaymentDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 2))
                ),
                Advance(
                    id: UUID(),
                    userId: UUID(),
                    amount: 100.0,
                    fee: 3.0,
                    status: "disbursed",
                    requestDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 2)),
                    repaymentDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(86400 * 5))
                )
            ]
            self?.outstandingBalance = 103.0
            self?.availableLimit = 147.0
            self?.isLoading = false
        }
    }

    func requestAdvance(amount: Double, reason: String) {
        let newAdvance = Advance(
            id: UUID(),
            userId: UUID(),
            amount: amount,
            fee: amount * 0.03,
            status: "pending",
            requestDate: ISO8601DateFormatter().string(from: Date()),
            repaymentDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(86400 * 7))
        )

        advances.insert(newAdvance, at: 0)
        availableLimit -= amount
        outstandingBalance += amount + (amount * 0.03)
    }
}

import Combine

#Preview {
    AdvanceView()
}
