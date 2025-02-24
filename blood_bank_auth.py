import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from datetime import datetime
import sqlite3
import hashlib
import json
from blood_bank_tkinter import BloodBankApp

class BloodBankAuth:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Bank Management System")
        self.root.geometry("1024x768")
        self.API_BASE_URL = "http://localhost:8000"
        
        # Initialize database
        self.init_database()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(pady=20, expand=True, fill='both')
        
        # Start with login view
        self.current_user = None
        self.user_role = None
        self.show_login()

    def init_database(self):
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                hospital_name TEXT,
                donor_id TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Blood Bank Login", 
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Username
        ttk.Label(self.main_frame, text="Username:").pack()
        username_entry = ttk.Entry(self.main_frame)
        username_entry.pack(pady=5)
        
        # Password
        ttk.Label(self.main_frame, text="Password:").pack()
        password_entry = ttk.Entry(self.main_frame, show="*")
        password_entry.pack(pady=5)
        
        # Login button
        ttk.Button(
            self.main_frame,
            text="Login",
            command=lambda: self.login(username_entry.get(), password_entry.get())
        ).pack(pady=10)
        
        # Register options
        ttk.Label(self.main_frame, text="Register as:").pack(pady=5)
        ttk.Button(self.main_frame, text="Hospital", 
                  command=lambda: self.show_register("hospital")).pack(pady=2)
        ttk.Button(self.main_frame, text="Donor", 
                  command=lambda: self.show_register("donor")).pack(pady=2)

    def show_register(self, role):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text=f"Register as {role.title()}", 
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Username
        ttk.Label(self.main_frame, text="Username:").pack()
        username_entry = ttk.Entry(self.main_frame)
        username_entry.pack(pady=5)
        
        # Email
        ttk.Label(self.main_frame, text="Email:").pack()
        email_entry = ttk.Entry(self.main_frame)
        email_entry.pack(pady=5)
        
        # Password
        ttk.Label(self.main_frame, text="Password:").pack()
        password_entry = ttk.Entry(self.main_frame, show="*")
        password_entry.pack(pady=5)
        
        # Role-specific fields
        extra_field_entry = None
        if role == "hospital":
            ttk.Label(self.main_frame, text="Hospital Name:").pack()
            extra_field_entry = ttk.Entry(self.main_frame)
            extra_field_entry.pack(pady=5)
        
        # Register button
        ttk.Button(
            self.main_frame,
            text="Register",
            command=lambda: self.register(
                username_entry.get(),
                email_entry.get(),
                password_entry.get(),
                role,
                extra_field_entry.get() if extra_field_entry else None
            )
        ).pack(pady=10)
        
        # Back to login
        ttk.Button(self.main_frame, text="Back to Login", 
                  command=self.show_login).pack(pady=5)

    def login(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, hospital_name, donor_id, password 
            FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[3] == self.hash_password(password):
            self.current_user = username
            self.user_role = result[0]
            if self.user_role == "admin":
                self.show_admin_dashboard()
            elif self.user_role == "hospital":
                self.show_hospital_dashboard(result[1])
            elif self.user_role == "donor":
                self.show_donor_dashboard(result[2])
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self, username, email, password, role, extra_field=None):
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if role == "hospital" and not extra_field:
            messagebox.showerror("Error", "Please enter hospital name")
            return
        
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, role, hospital_name, donor_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                username,
                email,
                self.hash_password(password),
                role,
                extra_field if role == "hospital" else None,
                None  # donor_id will be updated after donor registration
            ))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()

    def show_admin_dashboard(self):
        self.clear_frame()
        app = BloodBankApp(self.root, self.main_frame, self.current_user, "admin")
        
        # Add logout button
        ttk.Button(self.main_frame, text="Logout", 
                  command=self.logout).pack(pady=10)

    def show_hospital_dashboard(self, hospital_name):
        self.clear_frame()
        app = BloodBankApp(self.root, self.main_frame, self.current_user, "hospital", hospital_name)
        
        # Add logout button
        ttk.Button(self.main_frame, text="Logout", 
                  command=self.logout).pack(pady=10)

    def show_donor_dashboard(self, donor_id):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text=f"Welcome, {self.current_user}", 
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Donation history
        history_frame = ttk.LabelFrame(self.main_frame, text="Your Donation History")
        history_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        columns = ('Date', 'Blood Type', 'Quantity', 'Center')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(pady=10, fill='both', expand=True)
        
        # Load donation history
        self.load_donor_history(donor_id)
        
        # Add logout button
        ttk.Button(self.main_frame, text="Logout", 
                  command=self.logout).pack(pady=10)

    def load_donor_history(self, donor_id):
        try:
            response = requests.get(f'{self.API_BASE_URL}/donor-history/{donor_id}/')
            if response.status_code == 200:
                history = response.json()
                for donation in history:
                    self.history_tree.insert('', 'end', values=(
                        donation['date'],
                        donation['blood_type'],
                        donation['quantity'],
                        donation['center']
                    ))
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to fetch donation history")

    def logout(self):
        self.current_user = None
        self.user_role = None
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = BloodBankAuth(root)
    root.mainloop()
