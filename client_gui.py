# Client GUI program

import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

from config import *
from client import connect, send, receive


class ClientGUI:
    def __init__(self, root):
        # Window
        self.root = root
        self.root.title("Chat Client")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Get IP address and username
        self.server, self.username = self.prompt_for_login()
        if not self.username:
            self.root.destroy()
            return
        # Create client socket and login as username
        self.client_soc = connect(self.server)
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

        # Start
        self.running = True
        self.append_message(f"Connected as {self.username}.")
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()

    def prompt_for_login(self):
        self.root.withdraw()
        ip_address = simpledialog.askstring("Login", "Enter the server IP address to connect to:", parent=self.root)
        self.root.deiconify()
        self.root.withdraw()
        username = simpledialog.askstring("Login", "Enter a username:", parent=self.root)
        self.root.deiconify()
        ip_address = ip_address.strip()
        username = username.strip() if username else None
        return ip_address, username

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