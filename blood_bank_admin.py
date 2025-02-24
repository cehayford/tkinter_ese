from tkinter import ttk, messagebox
import sqlite3
import requests

class BloodBankAdmin:
    def __init__(self, parent):
        self.parent = parent
        self.setup_admin_view()

    def setup_admin_view(self):
        # Create admin tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(pady=10, expand=True, fill='both')

        self.dashboard_frame = ttk.Frame(self.notebook)
        self.donors_frame = ttk.Frame(self.notebook)
        self.hospitals_frame = ttk.Frame(self.notebook)
        self.requests_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.donors_frame, text="Donors")
        self.notebook.add(self.hospitals_frame, text="Hospitals")
        self.notebook.add(self.requests_frame, text="Blood Requests")
        
        self.setup_admin_dashboard()
        self.setup_donors_view()
        self.setup_hospitals_view()
        self.setup_requests_view()

    def setup_admin_dashboard(self):
        # Dashboard Header
        ttk.Label(self.dashboard_frame, text="Blood Bank Dashboard", 
                 font=('Arial', 20, 'bold')).pack(pady=20)
        
        # Create stats frames
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill='x', padx=20)
        
        # Statistics boxes
        stats = [
            ("Total Donors", "donor_count"),
            ("Available Blood Units", "blood_units"),
            ("Pending Requests", "pending_requests"),
            ("Centers", "center_count")
        ]
        
        for i, (label, stat_id) in enumerate(stats):
            stat_frame = ttk.LabelFrame(stats_frame, text=label)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            ttk.Label(stat_frame, text="Loading...", font=('Arial', 16)).pack(pady=20)
        
        # Refresh button
        ttk.Button(self.dashboard_frame, text="Refresh Dashboard",
                  command=self.refresh_dashboard).pack(pady=20)

    def setup_donors_view(self):
        # Donor List
        list_frame = ttk.LabelFrame(self.donors_frame, text="Donor List")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Create treeview
        columns = ('Name', 'Blood Type', 'Phone', 'Email', 'Location', 'Quantity', 'Hospital')
        self.donor_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.donor_tree.heading(col, text=col)
            self.donor_tree.column(col, width=100)
        
        self.donor_tree.pack(pady=10, fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.donor_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.donor_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load donors data
        self.refresh_donor_list()

    def setup_hospitals_view(self):
        # Hospital List
        list_frame = ttk.LabelFrame(self.hospitals_frame, text="Hospital List")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Create treeview
        columns = ('Hospital Name', 'Location', 'Phone', 'Email')
        self.hospital_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.hospital_tree.heading(col, text=col)
            self.hospital_tree.column(col, width=100)
        
        self.hospital_tree.pack(pady=10, fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.hospital_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.hospital_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load hospitals data
        self.refresh_hospital_list()

    def setup_requests_view(self):
        # Request List
        list_frame = ttk.LabelFrame(self.requests_frame, text="Blood Requests")
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Create treeview
        columns = ('Patient', 'Blood Type', 'Quantity', 'Hospital', 'Status', 'Created At')
        self.request_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.request_tree.heading(col, text=col)
            self.request_tree.column(col, width=100)
        
        self.request_tree.pack(pady=10, fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.request_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.request_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load requests data
        self.refresh_request_list()

    def refresh_dashboard(self):
        try:
            response = requests.get(f'{self.API_BASE_URL}/dashboard-stats/')
            if response.status_code == 200:
                stats = response.json()
                # Update dashboard statistics
                pass
            else:
                messagebox.showerror("Error", "Failed to fetch dashboard data")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to connect to server")

    def refresh_donor_list(self):
        # Clear existing items
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT donor_name, blood_type, phone, email, location, quantity_ml, hospital FROM donors')
            donors = cursor.fetchall()
            conn.close()
            
            for donor in donors:
                self.donor_tree.insert('', 'end', values=donor)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch donor list: {str(e)}")

    def refresh_hospital_list(self):
        # Clear existing items
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
        # Clear existing items
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT patient_name, blood_group, quantity_ml, hospital, status, created_at FROM blood_requests')
            requests_data = cursor.fetchall()
            conn.close()
            
            for req in requests_data:
                self.request_tree.insert('', 'end', values=req)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch request list: {str(e)}")
