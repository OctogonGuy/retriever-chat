# Client GUI program

import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

from config import *
from client import connect, send, receive


class ClientGUI:
    def __init__(self, root):
        # Window
        self.root = root
        self.root.title("Chat Client")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Get login info
        # Get username
        try:
            self.username = None
            while not self.username:
                self.username = self.prompt_for_username()
                if self.username is None:
                    raise AttributeError
                if not self.username:
                    self.root.withdraw()
                    messagebox.showerror("Username Error", "Invalid username")
                    self.root.deiconify()
        except AttributeError:
            exit(1)
        # Get IP address and create client socket
        try:
            self.server = self.prompt_for_ip_address()
            self.client_soc = connect(self.server)
        except AttributeError:
            exit(1)
        except Exception as e:
            self.root.withdraw()
            messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
            self.root.deiconify()
            exit(1)
        # Send username to server
        send(self.client_soc, self.username)

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", height=20, width=60)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Text box
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.message_entry = tk.Entry(self.entry_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.on_send)
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.on_send)
        self.send_button.pack(side=tk.RIGHT)

        # Start listening for messages
        self.running = True
        self.append_message(f"Connected as {self.username}.")
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()

    def prompt_for_ip_address(self):
        self.root.withdraw()
        ip_address = simpledialog.askstring("Login", "Enter the server IP address to connect to:", parent=self.root)
        self.root.deiconify()
        return ip_address.strip()

    def prompt_for_username(self):
        self.root.withdraw()
        username = simpledialog.askstring("Login", "Enter a username:", parent=self.root)
        self.root.deiconify()
        return username.strip()

    def append_message(self, message):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def on_send(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return
        send(self.client_soc, message)
        self.append_message(f"You: {message}")
        self.message_entry.delete(0, tk.END)

    def listen_for_messages(self):
        while self.running:
            try:
                message = receive(self.client_soc)
                if message:
                    self.root.after(0, self.append_message, message)
            except OSError:
                break

    def on_close(self):
        self.running = False
        send(self.client_soc, DISCONNECT_MESSAGE)
        self.root.after(100, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()