import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from blood_bank_admin import BloodBankAdmin 
import admin_update_entry


class BloodBankApp:
    def __init__(self, root, parent, username, role, hospital_name=None, logout_callback=None):
        self.root = root
        self.root.title("Blood Bank Management System")
        self.root.geometry("1024x768")
        self.parent = parent
        self.username = username
        self.role = role
        self.hospital_name = hospital_name
        self.logout_callback = logout_callback
        self.logout_frame = ttk.Frame(self.parent)
        self.logout_frame.pack(fill='x')

        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hospital_name
            FROM users where username = ?
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            hospital_name = result[0]

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(pady=0, expand=True, fill='both')
        if self.role == "admin":
            self.admin = BloodBankAdmin(self.parent)
        elif self.role == "hospital":
            self.setup_hospital_view()
        ttk.Button(self.logout_frame, text="Logout", command=self.logout).pack(pady=0, padx=10, anchor='ne')
        

    def logout(self):
        if self.logout_callback:
            self.logout_callback()
        else:
            self.root.destroy()


    def setup_hospital_view(self):
        self.donor_reg_frame = ttk.Frame(self.notebook)
        self.requests_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.donor_reg_frame, text="Register Donor")
        self.notebook.add(self.requests_frame, text="Blood Requests")
        
        self.setup_donor_management()
        self.setup_blood_requests()
        self.root.after(100, self.refresh_donor_list)

    def add_scrollbar(self, frame):
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    def setup_donor_management(self):
        form_frame = ttk.LabelFrame(self.donor_reg_frame, text="Add New Donor")
        form_frame.pack(padx=20, pady=10, fill='x')

        fields = [
            ("Donor Name:", "donor_name", ttk.Entry),
            ("Blood Type:", "blood_type", ttk.Combobox),
            ("Phone:", "phone", ttk.Entry),
            ("Email:", "email", ttk.Entry),
            ("Location:", "location", ttk.Entry),
            ("Quantity (ml):", "quantity_ml", ttk.Entry)
        ]
        
        self.donor_entries = {}
        for i, (label, field_name, widget) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            if widget == ttk.Combobox:
                self.donor_entries[field_name] = widget(form_frame, 
                    values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
            else:
                self.donor_entries[field_name] = widget(form_frame)
            self.donor_entries[field_name].grid(row=i, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Medical Report:").grid(row=len(fields), column=0)
        self.report_path = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.report_path).grid(row=len(fields), column=1)
        ttk.Button(form_frame, text="Browse", 
                  command=self.browse_file).grid(row=len(fields), column=2)
        
        ttk.Button(form_frame, text="Register Donor",
                  command=self.register_donor).grid(row=len(fields)+1, column=0, columnspan=3, pady=20)
        
        list_frame = ttk.LabelFrame(self.donor_reg_frame, text="Donor List")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        scrollable_frame = self.add_scrollbar(list_frame)

        columns = ('Name', 'Blood Type', 'Phone', 'Email', 'Location', 'Donor ID')
        self.donor_tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings')
        
        for col in columns:
            self.donor_tree.heading(col, text=col)
            self.donor_tree.column(col, width=100)
        
        self.donor_tree.pack(pady=4, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.donor_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.donor_tree.configure(yscrollcommand=scrollbar.set)
        
        ttk.Button(list_frame, text="Edit Donor", command=self.edit_donor).pack(side='left', padx=5, pady=5)
        ttk.Button(list_frame, text="Delete Donor", command=self.delete_donor).pack(side='left', padx=5, pady=5)


    def setup_blood_requests(self):
        form_frame = ttk.LabelFrame(self.requests_frame, text="New Blood Request")
        form_frame.pack(padx=20, pady=10, fill='x')
        
        fields = [
            ("Patient Name:", "patient_name", ttk.Entry),
            ("Blood Type:", "blood_type", ttk.Combobox),
            ("Quantity (ml):", "quantity_ml", ttk.Entry),
            ("Hospital:", "hospital", ttk.Entry),
            ("Location:", "location", ttk.Entry),

        ]
        
        self.request_entries = {}
        for i, (label, field_name, widget) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            if widget == ttk.Combobox:
                self.request_entries[field_name] = widget(form_frame, 
                    values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
            else:
                self.request_entries[field_name] = widget(form_frame)
            self.request_entries[field_name].grid(row=i, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Submit Request",
                  command=self.submit_request).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        list_frame = ttk.LabelFrame(self.requests_frame, text="Blood Requests")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        columns = ('Patient', 'Blood Type', 'Quantity', 'Hospital', 'Status', 'Created At', 'Request ID')
        self.request_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.request_tree.heading(col, text=col)
            self.request_tree.column(col, width=100)
        
        self.request_tree.pack(pady=4, fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.request_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.request_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(list_frame, text="Edit Request", command=self.edit_request).pack(side='left', padx=5, pady=5)
        ttk.Button(list_frame, text="Delete Request", command=self.delete_request).pack(side='left', padx=5, pady=5)

        self.refresh_request_list()

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.pdf")]
        )
        if filename:
            self.report_path.set(filename)

    def register_donor(self): 
        donor_data = {
            'donor_name': self.donor_entries['donor_name'].get(),
            'blood_type': self.donor_entries['blood_type'].get(),
            'phone': self.donor_entries['phone'].get(),
            'email': self.donor_entries['email'].get(),
            'location': self.donor_entries['location'].get(),
            'quantity_ml': self.donor_entries['quantity_ml'].get()
        }

        if not all(donor_data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            files = {'medical_report': open(self.report_path.get(), 'rb')} if self.report_path.get() else None

            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO donors (donor_name, blood_type, phone, email, location, quantity_ml, hospital, medical_report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                donor_data['donor_name'],
                donor_data['blood_type'],
                donor_data['phone'],
                donor_data['email'],
                donor_data['location'],
                donor_data['quantity_ml'],
                self.hospital_name,
                files['medical_report'].name if files else None
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Donor registered successfully!")
            self.clear_donor_form()
            self.refresh_donor_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def submit_request(self):
        request_data = {
            'patient_name': self.request_entries['patient_name'].get(),
            'blood_group': self.request_entries['blood_type'].get(),
            'quantity_ml': self.request_entries['quantity_ml'].get(),
            'hospital': self.request_entries['hospital'].get(),
            'location': self.request_entries['location'].get(),
        }
        
        if not all(request_data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blood_requests (patient_name, blood_group, quantity_ml, hospital, location)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                request_data['patient_name'],
                request_data['blood_group'],
                request_data['quantity_ml'],
                request_data['hospital'],
                request_data['location']
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Blood request submitted successfully!")
            self.clear_request_form()
            self.refresh_request_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def clear_donor_form(self):
        for entry in self.donor_entries.values():
            entry.delete(0, tk.END)
        self.report_path.set('')

    def clear_request_form(self):
        for entry in self.request_entries.values():
            entry.delete(0, tk.END)

    def refresh_donor_list(self):
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT donor_name, blood_type, phone, email, location, donor_id FROM donors')
            donors = cursor.fetchall()
            conn.close()
            
            for donor in donors:
                self.donor_tree.insert('', 'end', values=donor)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch donor list: {str(e)}")

    def refresh_request_list(self):
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT patient_name, blood_group, quantity_ml, hospital, status, created_at, request_id FROM blood_requests')
            requests_data = cursor.fetchall()
            conn.close()
            
            for req in requests_data:
                self.request_tree.insert('', 'end', values=req)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch request list: {str(e)}")

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

    def create_user(self, username, password, email, role, hospital_name=None, donor_id=None):
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, email, role, hospital_name, donor_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, email, role, hospital_name, donor_id))
        conn.commit()
        conn.close()

    def retrieve_user(self, username):
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    def update_user(self, username, password=None, email=None, role=None, hospital_name=None, donor_id=None):
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        if password:
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (password, username))
        if email:
            cursor.execute('UPDATE users SET email = ? WHERE username = ?', (email, username))
        if role:
            cursor.execute('UPDATE users SET role = ? WHERE username = ?', (role, username))
        if hospital_name:
            cursor.execute('UPDATE users SET hospital_name = ? WHERE username = ?', (hospital_name, username))
        if donor_id:
            cursor.execute('UPDATE users SET donor_id = ? WHERE username = ?', (donor_id, username))
        conn.commit()
        conn.close()

    def delete_user(self, username):
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()

    def setup_donors_view(self):
        list_frame = ttk.LabelFrame(self.donors_frame, text="Donor List")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ('Name', 'Blood Type', 'Phone', 'Email', 'Location', 'Quantity', 'Hospital')
        self.donor_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.donor_tree.heading(col, text=col)
            self.donor_tree.column(col, width=100)
        
        self.donor_tree.pack(pady=10, fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.donor_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.donor_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_donor_list()

    def setup_hospitals_view(self):
        list_frame = ttk.LabelFrame(self.hospitals_frame, text="Hospital List")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        columns = ('Hospital Name', 'Location', 'Phone', 'Email')
        self.hospital_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.hospital_tree.heading(col, text=col)
            self.hospital_tree.column(col, width=100)
        
        self.hospital_tree.pack(pady=10, fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.hospital_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.hospital_tree.configure(yscrollcommand=scrollbar.set)

        self.refresh_hospital_list()

    def setup_requests_view(self):
        list_frame = ttk.LabelFrame(self.requests_frame, text="Blood Requests")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ('Patient', 'Blood Type', 'Quantity', 'Hospital', 'Status', 'Created At')
        self.request_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.request_tree.heading(col, text=col)
            self.request_tree.column(col, width=100)
        
        self.request_tree.pack(pady=10, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.request_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.request_tree.configure(yscrollcommand=scrollbar.set)

        self.refresh_request_list()

    def refresh_donor_list(self):
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT donor_name, blood_type, phone, email, location, donor_id FROM donors')
            donors = cursor.fetchall()
            conn.close()
            
            for donor in donors:
                self.donor_tree.insert('', 'end', values=donor)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch donor list: {str(e)}")

    def refresh_hospital_list(self):
        for item in self.hospital_tree.get_children():
            self.hospital_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT hospital_name, location, phone, email FROM hospitals')
            hospitals = cursor.fetchall()
            conn.close()
            
            for hospital in hospitals:
                self.hospital_tree.insert('', 'end', values=hospital)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch hospital list: {str(e)}")

    def refresh_request_list(self):
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT patient_name, blood_group, quantity_ml, hospital, status, created_at, request_id FROM blood_requests')
            requests_data = cursor.fetchall()
            conn.close()
            
            for req in requests_data:
                self.request_tree.insert('', 'end', values=req)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch request list: {str(e)}")

    def edit_donor(self):
        admin_update_entry.show_edit_donor_form(self)

    def edit_request(self):
        admin_update_entry.show_edit_request_form(self)

    def delete_donor(self):
        selected_item = self.donor_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donor to delete")
            return
        
        donor_data = self.donor_tree.item(selected_item)['values']
        donor_id = donor_data[5]
        print(donor_id)
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM donors
                WHERE donor_id=?
            ''', (donor_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Donor deleted successfully!")
            self.refresh_donor_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete donor: {str(e)}")

    def delete_request(self):
        selected_item = self.request_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a request to delete")
            return
        
        request_data = self.request_tree.item(selected_item)['values']
        request_id= request_data[6]
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM blood_requests
                WHERE request_id=?
            ''', (request_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Blood request deleted successfully!")
            self.refresh_request_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete request: {str(e)}")

    def clear_frame(self):
        for widget in self.parent.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BloodBankApp(root)
    app.init_database()
    root.mainloop()
