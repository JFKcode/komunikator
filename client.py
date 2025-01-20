import socket
import threading
import tkinter as tk
from tkinter import messagebox


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Komunikator Klient")
        self.client_socket = None  # Gniazdo klienta
        self.username = None  # Nazwa użytkownika

        # Sekcja konfiguracji połączenia
        self.config_frame = tk.Frame(self.root)
        tk.Label(self.config_frame, text="IP serwera:").pack(side=tk.LEFT, padx=5)
        self.server_ip_entry = tk.Entry(self.config_frame, width=15)
        self.server_ip_entry.insert(0, "127.0.0.1")  # Domyślny IP serwera
        self.server_ip_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(self.config_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.server_port_entry = tk.Entry(self.config_frame, width=5)
        self.server_port_entry.insert(0, "1234")  # Domyślny port serwera
        self.server_port_entry.pack(side=tk.LEFT, padx=5)
        self.connect_button = tk.Button(self.config_frame, text="Połącz", command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.config_frame.pack(pady=10)

        # Pole do wprowadzenia nazwy użytkownika
        self.username_frame = tk.Frame(self.root)
        tk.Label(self.username_frame, text="Nazwa użytkownika:").pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(self.username_frame, width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        self.username_frame.pack(pady=5)

        # Okno wiadomości
        self.messages_frame = tk.Frame(self.root)
        self.scrollbar = tk.Scrollbar(self.messages_frame)
        self.msg_list = tk.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.messages_frame.pack()

        # Duże pole wprowadzania wiadomości
        self.entry_field = tk.Text(self.root, height=5, width=50)
        self.entry_field.pack(padx=5, pady=5)
        self.send_button = tk.Button(self.root, text="Wyślij", command=self.send_message, state=tk.DISABLED)
        self.send_button.pack(pady=5)

        # Informacja o statusie połączenia
        self.status_label = tk.Label(self.root, text="Niepołączony", fg="red")
        self.status_label.pack(pady=5)

        # Obsługa zamykania okna
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def connect_to_server(self):
        # Pobieranie IP, portu serwera i nazwy użytkownika
        server_ip = self.server_ip_entry.get()
        server_port = int(self.server_port_entry.get())
        self.username = self.username_entry.get().strip()

        if not self.username:
            messagebox.showerror("Błąd", "Nazwa użytkownika nie może być pusta.")
            return

        try:
            # Nawiązywanie połączenia z serwerem
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))
            self.status_label.config(text="Połączony z serwerem", fg="green")
            self.send_button.config(state=tk.NORMAL)
            self.connect_button.config(state=tk.DISABLED)
            self.username_entry.config(state=tk.DISABLED)

            # Wątek odbierający wiadomości od serwera
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można połączyć z serwerem: {e}")

    def receive_messages(self):
        # Odbieranie wiadomości od serwera
        while True:
            try:
                msg = self.client_socket.recv(1024).decode("utf-8")
                if msg:
                    self.msg_list.insert(tk.END, f"Serwer: {msg}")
                    self.msg_list.insert(tk.END, "-" * 50)  # Kreska oddzielająca
                else:
                    break
            except:
                break

    def send_message(self):
        # Wysyłanie wiadomości do serwera
        msg = self.entry_field.get("1.0", tk.END).strip()
        if msg:
            try:
                # Dodanie nazwy użytkownika do wiadomości
                full_message = f"{self.username}: {msg}"
                self.client_socket.sendall(full_message.encode("utf-8"))

                # Wyświetlenie wiadomości w oknie klienta
                self.msg_list.insert(tk.END, f"Ty: {msg}")
                self.msg_list.insert(tk.END, "-" * 50)  # Kreska oddzielająca
                self.entry_field.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wysłać wiadomości: {e}")

    def on_close(self):
        # Zamknięcie połączenia przy zamykaniu aplikacji
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
