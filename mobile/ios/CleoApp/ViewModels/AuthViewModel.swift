import Foundation
import Combine

class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()
    private let authService = AuthService.shared

    func checkAuthentication() {
        if let _ = KeychainHelper.shared.getAccessToken() {
            isAuthenticated = true
            loadCurrentUser()
        }
    }

    func login(email: String, password: String) {
        guard !email.isEmpty, !password.isEmpty else {
            errorMessage = "Please enter email and password"
            return
        }

        isLoading = true
        errorMessage = nil

        authService.login(email: email, password: password)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] response in
                    KeychainHelper.shared.saveTokens(
                        accessToken: response.accessToken,
                        refreshToken: response.refreshToken
                    )
                    self?.currentUser = response.user
                    self?.isAuthenticated = true
                }
            )
            .store(in: &cancellables)
    }

    func register(email: String, password: String, fullName: String) {
        guard !email.isEmpty, !password.isEmpty, !fullName.isEmpty else {
            errorMessage = "Please fill in all fields"
            return
        }

        isLoading = true
        errorMessage = nil

        authService.register(email: email, password: password, fullName: fullName)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] response in
                    KeychainHelper.shared.saveTokens(
                        accessToken: response.accessToken,
                        refreshToken: response.refreshToken
                    )
                    self?.currentUser = response.user
                    self?.isAuthenticated = true
                }
            )
            .store(in: &cancellables)
    }

    func logout() {
        KeychainHelper.shared.clearTokens()
        currentUser = nil
        isAuthenticated = false
    }

    private func loadCurrentUser() {
        authService.getCurrentUser()
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure = completion {
                        self?.logout()
                    }
                },
                receiveValue: { [weak self] user in
                    self?.currentUser = user
                }
            )
            .store(in: &cancellables)
    }
}
