import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var messageText = ""

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Personality Selector
                PersonalitySelector(selectedPersonality: $viewModel.selectedPersonality)
                    .padding()
                    .background(Color(.systemGroupedBackground))

                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: viewModel.messages.count) { _ in
                        if let lastMessage = viewModel.messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }

                // Input Bar
                HStack(spacing: 12) {
                    TextField("Ask Cleo anything...", text: $messageText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())

                    Button(action: {
                        sendMessage()
                    }) {
                        Image(systemName: "arrow.up.circle.fill")
                            .font(.title2)
                            .foregroundColor(messageText.isEmpty ? .gray : Color(hex: "667EEA"))
                    }
                    .disabled(messageText.isEmpty || viewModel.isLoading)
                }
                .padding()
                .background(Color(.systemBackground))
            }
            .navigationTitle("Chat with Cleo")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private func sendMessage() {
        let text = messageText
        messageText = ""
        viewModel.sendMessage(text)
    }
}

struct PersonalitySelector: View {
    @Binding var selectedPersonality: String

    let personalities = ["supportive", "funny", "strict", "roast"]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(personalities, id: \.self) { personality in
                    Button(action: {
                        selectedPersonality = personality
                    }) {
                        VStack(spacing: 6) {
                            Image(systemName: iconForPersonality(personality))
                                .font(.title3)

                            Text(personality.capitalized)
                                .font(.caption)
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(selectedPersonality == personality ? Color(hex: "667EEA") : Color(.systemGray5))
                        .foregroundColor(selectedPersonality == personality ? .white : .primary)
                        .cornerRadius(12)
                    }
                }
            }
        }
    }

    func iconForPersonality(_ personality: String) -> String {
        switch personality {
        case "supportive": return "heart.fill"
        case "funny": return "face.smiling.fill"
        case "strict": return "exclamationmark.triangle.fill"
        case "roast": return "flame.fill"
        default: return "face.smiling"
        }
    }
}

struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.role == "user" {
                Spacer()
            }

            VStack(alignment: message.role == "user" ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(12)
                    .background(message.role == "user" ? Color(hex: "667EEA") : Color(.systemGray5))
                    .foregroundColor(message.role == "user" ? .white : .primary)
                    .cornerRadius(16)

                Text(formatTime(message.timestamp))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

            if message.role == "assistant" {
                Spacer()
            }
        }
    }

    func formatTime(_ timestamp: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: timestamp) {
            let timeFormatter = DateFormatter()
            timeFormatter.timeStyle = .short
            return timeFormatter.string(from: date)
        }
        return ""
    }
}

class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var selectedPersonality = "supportive"
    @Published var isLoading = false

    private let chatService = ChatService.shared
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Add welcome message
        messages.append(ChatMessage(
            id: UUID(),
            role: "assistant",
            content: "Hey! I'm Cleo, your AI financial assistant. How can I help you today?",
            timestamp: ISO8601DateFormatter().string(from: Date())
        ))
    }

    func sendMessage(_ text: String) {
        // Add user message
        let userMessage = ChatMessage(
            id: UUID(),
            role: "user",
            content: text,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        messages.append(userMessage)

        isLoading = true

        chatService.sendMessage(text)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.addErrorMessage(error.localizedDescription)
                    }
                },
                receiveValue: { [weak self] response in
                    self?.messages.append(response.message)
                }
            )
            .store(in: &cancellables)
    }

    private func addErrorMessage(_ error: String) {
        messages.append(ChatMessage(
            id: UUID(),
            role: "assistant",
            content: "Sorry, I encountered an error: \(error)",
            timestamp: ISO8601DateFormatter().string(from: Date())
        ))
    }
}

import Combine

#Preview {
    ChatView()
}
