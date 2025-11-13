import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel

    var body: some View {
        NavigationView {
            List {
                Section {
                    HStack {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(Color(hex: "667EEA"))

                        VStack(alignment: .leading, spacing: 4) {
                            Text(authViewModel.currentUser?.fullName ?? "User")
                                .font(.title3)
                                .fontWeight(.semibold)

                            Text(authViewModel.currentUser?.email ?? "")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            Text(authViewModel.currentUser?.subscriptionTier.capitalized ?? "Free")
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color(hex: "667EEA").opacity(0.2))
                                .foregroundColor(Color(hex: "667EEA"))
                                .cornerRadius(8)
                        }
                    }
                    .padding(.vertical, 8)
                }

                Section("Account") {
                    NavigationLink(destination: Text("Subscription Details")) {
                        Label("Subscription", systemImage: "star.fill")
                    }

                    NavigationLink(destination: Text("Personality Settings")) {
                        Label("Personality", systemImage: "face.smiling")
                    }

                    NavigationLink(destination: Text("Notifications")) {
                        Label("Notifications", systemImage: "bell.fill")
                    }
                }

                Section("Financial Services") {
                    NavigationLink(destination: Text("Advances")) {
                        Label("Cash Advances", systemImage: "bolt.fill")
                    }

                    NavigationLink(destination: Text("Credit Builder")) {
                        Label("Credit Builder", systemImage: "creditcard.fill")
                    }

                    NavigationLink(destination: Text("Analytics")) {
                        Label("Analytics", systemImage: "chart.bar.fill")
                    }
                }

                Section("Support") {
                    NavigationLink(destination: Text("Help Center")) {
                        Label("Help Center", systemImage: "questionmark.circle")
                    }

                    NavigationLink(destination: Text("Privacy")) {
                        Label("Privacy", systemImage: "lock.fill")
                    }

                    NavigationLink(destination: Text("About")) {
                        Label("About", systemImage: "info.circle")
                    }
                }

                Section {
                    Button(action: {
                        authViewModel.logout()
                    }) {
                        HStack {
                            Image(systemName: "rectangle.portrait.and.arrow.right")
                            Text("Log Out")
                        }
                        .foregroundColor(.red)
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(AuthViewModel())
}
