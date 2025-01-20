#include <iostream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <signal.h>
#include <wait.h>

// Funkcja obsługująca sygnał zakończenia procesów dziecka (SIGCHLD)
void handle_sigchld(int signo) {
    while (waitpid(-1, nullptr, WNOHANG) > 0) {} // Oczekuje na zakończenie procesów
}

int main() {
    const int PORT = 1234;                  // Port, na którym serwer nasłuchuje
    const char* SERVER_IP = "127.0.0.1";    // Adres IP serwera (localhost)
    int server_fd, client_fd;               // Deskryptory gniazd serwera i klienta
    sockaddr_in server_addr{}, client_addr{}; // Struktury adresów serwera i klienta
    socklen_t client_len = sizeof(client_addr); // Rozmiar struktury adresu klienta

    // Rejestracja funkcji obsługującej SIGCHLD
    signal(SIGCHLD, handle_sigchld);

    // Tworzenie gniazda serwera
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Konfiguracja adresu serwera
    server_addr.sin_family = AF_INET;        // IPv4
    server_addr.sin_port = htons(PORT);      // Port w porządku sieciowym
    inet_aton(SERVER_IP, &server_addr.sin_addr); // Konwersja adresu IP do struktury

    // Bindowanie gniazda serwera do adresu i portu
    if (bind(server_fd, (sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Rozpoczęcie nasłuchiwania na gnieździe serwera
    if (listen(server_fd, 10) == -1) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    std::cout << "Serwer nasłuchuje na " << SERVER_IP << ":" << PORT << std::endl;

    // Pętla obsługująca połączenia klientów
    while (true) {
        // Akceptowanie nowego połączenia
        client_fd = accept(server_fd, (sockaddr*)&client_addr, &client_len);
        if (client_fd == -1) {
            perror("Accept failed");
            continue;
        }

        std::cout << "Nowe połączenie od " << inet_ntoa(client_addr.sin_addr) << std::endl;

        if (fork() == 0) { // Proces dziecka
            close(server_fd); // Proces dziecka nie potrzebuje deskryptora serwera

            char buffer[1024] = {0}; // Bufor na dane od klienta
            while (true) {
                // Odbieranie danych od klienta
                ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
                if (bytes_read <= 0) {
                    std::cout << "Klient zakończył połączenie." << std::endl;
                    break; // Zakończenie połączenia
                }

                buffer[bytes_read] = '\0'; // Dodanie znaku końca stringa
                std::cout << "Otrzymano: " << buffer << std::endl;

                // Odesłanie potwierdzenia do klienta
                std::string response = "Serwer odpowiada: " + std::string(buffer);
                write(client_fd, response.c_str(), response.size());
            }

            close(client_fd); // Zamknięcie połączenia z klientem
            exit(0);          // Zakończenie procesu dziecka
        } else {
            close(client_fd); // Proces rodzica zamyka deskryptor klienta
        }
    }

    close(server_fd); // Zamknięcie gniazda serwera
    return 0;
}
