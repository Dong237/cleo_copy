import SwiftUI

struct CreditView: View {
    @StateObject private var viewModel = CreditViewModel()
    @State private var showingEnroll = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    if viewModel.isEnrolled {
                        // Credit Score Card
                        CreditScoreCard(
                            score: viewModel.creditScore?.score ?? 0,
                            change: viewModel.creditScore?.change ?? 0,
                            grade: viewModel.creditScore?.grade ?? "N/A"
                        )
                        .padding(.horizontal)

                        // Score Factors
                        ScoreFactorsSection(factors: viewModel.creditScore?.factors ?? [:])
                            .padding(.horizontal)

                        // Credit Activity
                        if !viewModel.activities.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Recent Activity")
                                    .font(.title3)
                                    .fontWeight(.bold)
                                    .padding(.horizontal)

                                ForEach(viewModel.activities) { activity in
                                    CreditActivityCard(activity: activity)
                                        .padding(.horizontal)
                                }
                            }
                        }
                    } else {
                        // Not Enrolled State
                        NotEnrolledView()
                            .padding(.horizontal)

                        Button(action: {
                            showingEnroll = true
                        }) {
                            HStack {
                                Image(systemName: "star.fill")
                                Text("Start Building Credit")
                                    .fontWeight(.semibold)
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color(hex: "667EEA"))
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .padding(.horizontal)
                    }
                }
                .padding(.vertical)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Credit Builder")
            .sheet(isPresented: $showingEnroll) {
                EnrollCreditView(viewModel: viewModel)
            }
            .onAppear {
                viewModel.loadCreditData()
            }
        }
    }
}

struct CreditScoreCard: View {
    let score: Int
    let change: Int
    let grade: String

    var scoreColor: Color {
        switch score {
        case 750...: return .green
        case 700..<750: return Color(hex: "667EEA")
        case 650..<700: return .orange
        default: return .red
        }
    }

    var body: some View {
        VStack(spacing: 20) {
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Credit Score")
                        .font(.headline)
                        .foregroundColor(.white.opacity(0.9))

                    Text("\(score)")
                        .font(.system(size: 64, weight: .bold, design: .rounded))
                        .foregroundColor(.white)

                    HStack(spacing: 4) {
        Image(systemName: change >= 0 ? "arrow.up.right" : "arrow.down.right")
                            .font(.caption)

                        Text("\(abs(change)) points")
                            .font(.subheadline)
                    }
                    .foregroundColor(.white.opacity(0.9))
                }

                Spacer()

                VStack(spacing: 8) {
                    ZStack {
                        Circle()
                            .stroke(Color.white.opacity(0.3), lineWidth: 8)
                            .frame(width: 80, height: 80)

                        Circle()
                            .trim(from: 0, to: CGFloat(score) / 850.0)
                            .stroke(Color.white, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                            .frame(width: 80, height: 80)
                            .rotationEffect(.degrees(-90))

                        Text(grade)
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    }

                    Text("Grade")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                }
            }

            // Score Range
            VStack(spacing: 8) {
                HStack {
                    Text("Poor")
                        .font(.caption2)
                    Spacer()
                    Text("Fair")
                        .font(.caption2)
                    Spacer()
                    Text("Good")
                        .font(.caption2)
                    Spacer()
                    Text("Excellent")
                        .font(.caption2)
                }
                .foregroundColor(.white.opacity(0.8))

                GeometryReader { geometry in
                    ZStack(alignment: .leading) {
                        // Background gradient
                        LinearGradient(
                            colors: [.red, .orange, .yellow, .green],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                        .frame(height: 8)
                        .cornerRadius(4)

                        // Score indicator
                        Circle()
                            .fill(Color.white)
                            .frame(width: 16, height: 16)
                            .offset(x: (geometry.size.width - 16) * (CGFloat(score) / 850.0))
                    }
                }
                .frame(height: 16)

                HStack {
                    Text("300")
                        .font(.caption2)
                    Spacer()
                    Text("850")
                        .font(.caption2)
                }
                .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [scoreColor, scoreColor.opacity(0.7)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(15)
        .shadow(radius: 3)
    }
}

struct ScoreFactorsSection: View {
    let factors: [String: Double]

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Score Factors")
                .font(.headline)

            VStack(spacing: 12) {
                ScoreFactor(
                    title: "Payment History",
                    percentage: factors["payment_history"] ?? 0,
                    icon: "clock.fill"
                )

                ScoreFactor(
                    title: "Credit Utilization",
                    percentage: factors["credit_utilization"] ?? 0,
                    icon: "percent"
                )

                ScoreFactor(
                    title: "Credit Age",
                    percentage: factors["credit_age"] ?? 0,
                    icon: "calendar"
                )

                ScoreFactor(
                    title: "Credit Mix",
                    percentage: factors["credit_mix"] ?? 0,
                    icon: "square.grid.2x2"
                )

                ScoreFactor(
                    title: "New Credit",
                    percentage: factors["new_credit"] ?? 0,
                    icon: "sparkles"
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct ScoreFactor: View {
    let title: String
    let percentage: Double
    let icon: String

    var color: Color {
        switch percentage {
        case 80...: return .green
        case 60..<80: return Color(hex: "667EEA")
        case 40..<60: return .orange
        default: return .red
        }
    }

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                    .frame(width: 24)

                Text(title)
                    .font(.subheadline)

                Spacer()

                Text("\(Int(percentage))%")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(color)
            }

            ProgressView(value: percentage / 100)
                .tint(color)
        }
    }
}

struct CreditActivityCard: View {
    let activity: CreditActivity

    var activityIcon: String {
        switch activity.activityType {
        case "payment":
            return "checkmark.circle.fill"
        case "inquiry":
            return "magnifyingglass.circle.fill"
        case "account_opened":
            return "plus.circle.fill"
        case "score_update":
            return "arrow.up.circle.fill"
        default:
            return "circle.fill"
        }
    }

    var activityColor: Color {
        switch activity.activityType {
        case "payment":
            return .green
        case "inquiry":
            return .orange
        case "account_opened":
            return .blue
        case "score_update":
            return Color(hex: "667EEA")
        default:
            return .gray
        }
    }

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: activityIcon)
                .font(.title3)
                .foregroundColor(activityColor)
                .frame(width: 40, height: 40)
                .background(activityColor.opacity(0.1))
                .cornerRadius(10)

            VStack(alignment: .leading, spacing: 4) {
                Text(activity.description)
                    .font(.subheadline)
                    .fontWeight(.medium)

                if let date = activity.date {
                    Text(formatDate(date))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            if let impact = activity.impact, impact != 0 {
                Text("\(impact > 0 ? "+" : "")\(impact)")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(impact > 0 ? .green : .red)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background((impact > 0 ? Color.green : Color.red).opacity(0.1))
                    .cornerRadius(6)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
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

struct NotEnrolledView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "chart.line.uptrend.xyaxis")
                .font(.system(size: 80))
                .foregroundColor(Color(hex: "667EEA"))

            Text("Build Your Credit")
                .font(.title)
                .fontWeight(.bold)

            Text("Start building credit history with our Credit Builder program")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)

            VStack(alignment: .leading, spacing: 16) {
                BenefitRow(icon: "checkmark.circle.fill", text: "No hard credit check")
                BenefitRow(icon: "checkmark.circle.fill", text: "Build credit while you save")
                BenefitRow(icon: "checkmark.circle.fill", text: "Track your progress monthly")
                BenefitRow(icon: "checkmark.circle.fill", text: "Report to all 3 credit bureaus")
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
        }
        .padding()
    }
}

struct BenefitRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.green)

            Text(text)
                .font(.subheadline)
        }
    }
}

struct EnrollCreditView: View {
    @ObservedObject var viewModel: CreditViewModel
    @Environment(\.dismiss) var dismiss

    @State private var monthlyAmount = "25"
    @State private var agreedToTerms = false

    let amounts = ["10", "25", "50", "100"]

    var body: some View {
        NavigationView {
            Form {
                Section("How It Works") {
                    Text("Credit Builder helps you build credit by making small monthly payments. Your payments are reported to credit bureaus, helping improve your credit score over time.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Section("Monthly Contribution") {
                    Picker("Amount", selection: $monthlyAmount) {
                        ForEach(amounts, id: \.self) { amount in
                            Text("$\(amount)/month")
                        }
                    }
                    .pickerStyle(.segmented)

                    VStack(alignment: .leading, spacing: 8) {
                        Text("This amount will be:")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        HStack {
                            Image(systemName: "1.circle.fill")
                                .foregroundColor(Color(hex: "667EEA"))
                            Text("Held in a secure savings account")
                                .font(.caption)
                        }

                        HStack {
                            Image(systemName: "2.circle.fill")
                                .foregroundColor(Color(hex: "667EEA"))
                            Text("Reported as on-time payments")
                                .font(.caption)
                        }

                        HStack {
                            Image(systemName: "3.circle.fill")
                                .foregroundColor(Color(hex: "667EEA"))
                            Text("Returned to you after 12 months")
                                .font(.caption)
                        }
                    }
                    .padding(.vertical, 8)
                }

                Section("Expected Results") {
                    if let amount = Double(monthlyAmount) {
                        VStack(spacing: 12) {
                            ResultRow(
                                title: "12-Month Savings",
                                value: "$\(amount * 12, specifier: "%.0f")"
                            )

                            ResultRow(
                                title: "Expected Score Increase",
                                value: "+35-50 points"
                            )

                            ResultRow(
                                title: "Credit Bureaus",
                                value: "Equifax, Experian, TransUnion"
                            )
                        }
                    }
                }

                Section {
                    Toggle(isOn: $agreedToTerms) {
                        Text("I agree to the Credit Builder terms and conditions")
                            .font(.subheadline)
                    }
                }
            }
            .navigationTitle("Enroll in Credit Builder")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Enroll") {
                        if let amount = Double(monthlyAmount) {
                            viewModel.enrollInCreditBuilder(monthlyAmount: amount)
                            dismiss()
                        }
                    }
                    .disabled(!agreedToTerms)
                }
            }
        }
    }
}

struct ResultRow: View {
    let title: String
    let value: String

    var body: some View {
        HStack {
            Text(title)
                .font(.subheadline)
            Spacer()
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(Color(hex: "667EEA"))
        }
    }
}

class CreditViewModel: ObservableObject {
    @Published var isEnrolled = false
    @Published var creditScore: CreditScore?
    @Published var activities: [CreditActivity] = []
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    func loadCreditData() {
        isLoading = true

        // Mock data for demo
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            // Simulate enrolled user
            self?.isEnrolled = true
            self?.creditScore = CreditScore(
                id: UUID(),
                userId: UUID(),
                score: 720,
                change: 15,
                grade: "B+",
                factors: [
                    "payment_history": 85.0,
                    "credit_utilization": 65.0,
                    "credit_age": 70.0,
                    "credit_mix": 60.0,
                    "new_credit": 55.0
                ],
                lastUpdated: ISO8601DateFormatter().string(from: Date())
            )

            self?.activities = [
                CreditActivity(
                    id: UUID(),
                    userId: UUID(),
                    activityType: "payment",
                    description: "Credit Builder payment reported",
                    impact: 5,
                    date: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 2))
                ),
                CreditActivity(
                    id: UUID(),
                    userId: UUID(),
                    activityType: "score_update",
                    description: "Credit score updated",
                    impact: 10,
                    date: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 7))
                ),
                CreditActivity(
                    id: UUID(),
                    userId: UUID(),
                    activityType: "payment",
                    description: "On-time payment recorded",
                    impact: 3,
                    date: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-86400 * 32))
                )
            ]

            self?.isLoading = false
        }
    }

    func enrollInCreditBuilder(monthlyAmount: Double) {
        isEnrolled = true
        creditScore = CreditScore(
            id: UUID(),
            userId: UUID(),
            score: 650,
            change: 0,
            grade: "C",
            factors: [
                "payment_history": 50.0,
                "credit_utilization": 60.0,
                "credit_age": 40.0,
                "credit_mix": 45.0,
                "new_credit": 70.0
            ],
            lastUpdated: ISO8601DateFormatter().string(from: Date())
        )
    }
}

import Combine

#Preview {
    CreditView()
}
