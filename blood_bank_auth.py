import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import logging
from blood_bank_tkinter import BloodBankApp


class BloodBankAuth:
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Bank Management System")
        self.root.geometry("1024x768")

        self.init_database()

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(pady=20, expand=True, fill='both')

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
        ttk.Label(self.main_frame, text="Blood Bank Sign-In", font=('Helvetica', 16, 'bold')).pack(pady=10)
        ttk.Label(self.main_frame, text="Username:").pack()
        username_entry = ttk.Entry(self.main_frame)
        username_entry.pack(pady=5)
        ttk.Label(self.main_frame, text="Password:").pack()
        password_entry = ttk.Entry(self.main_frame, show="*")
        password_entry.pack(pady=5)

        ttk.Button(self.main_frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get())).pack(pady=10)

        ttk.Label(self.main_frame, text="Register as:").pack(pady=5)
        ttk.Button(self.main_frame, text="Hospital", 
                  command=lambda: self.show_register("hospital")).pack(pady=2)
        ttk.Button(self.main_frame, text="Donor", 
                  command=lambda: self.show_register("donor")).pack(pady=2)


    def show_register(self, role):
        self.clear_frame()
        ttk.Label(self.main_frame, text=f"Register as {role.title()}", font=('Helvetica', 16, 'bold')).pack(pady=10)
        ttk.Label(self.main_frame, text="Username:").pack()
        username_entry = ttk.Entry(self.main_frame)
        username_entry.pack(pady=5)
        ttk.Label(self.main_frame, text="Email:").pack()
        email_entry = ttk.Entry(self.main_frame)
        email_entry.pack(pady=5)
        ttk.Label(self.main_frame, text="Password:").pack()
        password_entry = ttk.Entry(self.main_frame, show="*")
        password_entry.pack(pady=5)

        extra_field_entry = None
        
        if role == "hospital":
            ttk.Label(self.main_frame, text="Hospital Name:").pack()
            extra_field_entry = ttk.Entry(self.main_frame)
            extra_field_entry.pack(pady=5)
        if role == "donor":
            ttk.Label(self.main_frame, text="Donor ID:").pack()
            extra_field_entry = ttk.Entry(self.main_frame)
            extra_field_entry.pack(pady=5)
            print(extra_field_entry)

        ttk.Button(self.main_frame, text="Register", command=lambda: self.register(username_entry.get(), email_entry.get(), password_entry.get(), role, extra_field_entry.get())).pack(pady=10)
        ttk.Button(self.main_frame, text="Back to Login", command=self.show_login).pack(pady=5)


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
                extra_field if role == "donor" else None
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


    def show_hospital_dashboard(self, hospital_name):
        self.clear_frame()
        # ttk.Label(self.main_frame, text=f"{hospital_name}", font=('Helvetica', 18)).pack(pady=2, anchor='nw')
        app = BloodBankApp(self.root, self.main_frame, self.current_user, "hospital", hospital_name)


    def show_donor_dashboard(self, donor_id):
        self.clear_frame()
        ttk.Label(self.main_frame, text=f"Welcome, {self.current_user}.\n Donor Official Dashboard", 
                 font=('Helvetica', 16, 'bold')).pack(pady=10)

        history_frame = ttk.LabelFrame(self.main_frame, text="Your Donation History")
        history_frame.pack(padx=20, pady=10, fill='both', expand=True)
        columns = ('Date', 'Blood Type', 'Quantity', 'Center')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(pady=10, fill='both', expand=True)
        self.load_donor_history(donor_id)
        ttk.Button(self.main_frame, text="Logout", command=self.logout).pack(pady=0, padx=10, anchor='ne')


    def load_donor_history(self, donor_id):
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT last_donation, blood_type, quantity_ml, hospital
                FROM donors WHERE donor_id = ?
            ''', (donor_id,))
            history = cursor.fetchall()
            conn.close()
            for donation in history:
                self.history_tree.insert('', 'end', values=donation)
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            messagebox.showerror("Error", "Failed to fetch donation history")


    def logout(self):
        self.current_user = None
        self.user_role = None
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = BloodBankAuth(root)
    root.mainloop()
