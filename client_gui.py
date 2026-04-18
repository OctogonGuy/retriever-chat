# Client GUI program

import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

from config import *
# Import our clean connection and messaging tools from client.py!
from client import setup_connection, send, receive

class ClientGUI:
    def __init__(self, root):
        # Window setup
        self.root = root
        self.root.title("Secure Chat Client")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Hide the main chat window while we handle the login popups
        self.root.withdraw() 

        # 1. Connect to the Server using Auto-Discovery
        self.client_soc = setup_connection()
        if not self.client_soc:
            messagebox.showerror("Connection Error", "Server not found on the network. Please ensure the server is broadcasting.")
            self.root.destroy()
            return

        # 2. Authenticate using our new GUI-specific 3-try loop
        if not self.authenticate_gui():
            self.client_soc.close()
            self.root.destroy()
            return

        # 3. Get Username
        self.username = self.prompt_for_username()
        if not self.username:
            self.client_soc.close()
            self.root.destroy()
            return

        # Send the username to the server to officially join
        send(self.username, self.client_soc)

        # --- Show the Main Chat Window ---
        self.root.deiconify() 

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", height=20, width=60)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Text box area
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.message_entry = tk.Entry(self.entry_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.on_send)
        
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.on_send)
        self.send_button.pack(side=tk.RIGHT)

        # Start the background listener thread
        self.running = True
        self.append_message(f"--- Connected to secure room as {self.username} ---")
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()

    def authenticate_gui(self):
        """Handles the 3-try password loop using Tkinter popup boxes."""
        for attempt in range(3):
            # show='*' hides the password characters with asterisks
            password = simpledialog.askstring("Authentication", 
                                              f"Enter room password (Attempt {attempt+1}/3):", 
                                              parent=self.root, show='*')
            
            if password is None: # Triggers if they click "Cancel"
                return False

            send(password, self.client_soc)
            response = receive(self.client_soc)

            if response == "PASS_OK":
                messagebox.showinfo("Success", "Access granted!")
                return True
            elif response == "WRONG_PASS":
                messagebox.showwarning("Error", "Incorrect password. Try again.")
            elif response == "LOCKED_OUT":
                messagebox.showerror("Locked Out", "Incorrect password. You have been locked out.")
                return False
                
        return False

    def prompt_for_username(self):
        username = simpledialog.askstring("Login", "Enter your username:", parent=self.root)
        return username.strip() if username else None

    def append_message(self, message):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def on_send(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # Pass self.client_soc to the imported send function
        send(message, self.client_soc)
        self.append_message(f"You: {message}")
        self.message_entry.delete(0, tk.END)

    def listen_for_messages(self):
        while self.running:
            try:
                # Pass self.client_soc to the imported receive function
                message = receive(self.client_soc)
                if message:
                    # Tkinter requires GUI updates to happen safely via .after()
                    self.root.after(0, self.append_message, message)
            except OSError:
                break

    def on_close(self):
        self.running = False
        try:
            send(DISCONNECT_MESSAGE, self.client_soc)
        except Exception:
            pass
        self.root.after(100, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()