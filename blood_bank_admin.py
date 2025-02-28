from tkinter import ttk, messagebox
import sqlite3
import admin_approval as approve_frame

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
        
        self.notebook.add(self.dashboard_frame, text="Admin Dashboard")
        self.notebook.add(self.donors_frame, text="Donors")
        self.notebook.add(self.hospitals_frame, text="Hospitals")
        self.notebook.add(self.requests_frame, text="Patient Requests")
        
        self.setup_admin_dashboard()
        self.setup_donors_view()
        self.setup_hospitals_view()
        self.setup_requests_view()
        approve_frame.setup_request_approval(self)


    def setup_admin_dashboard(self):
        ttk.Label(self.dashboard_frame, text="Adminstrator Dashboard", 
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
        ttk.Button(self.dashboard_frame, text="Refresh",
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
        columns = ('Hospital Name', 'Email')
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
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            
            # Get total donors count
            cursor.execute('SELECT COUNT(*) FROM donors')
            donor_count = cursor.fetchone()[0]
            
            # Get available blood units (sum of all quantities)
            cursor.execute('SELECT COALESCE(SUM(quantity_ml), 0) FROM donors')
            blood_units = cursor.fetchone()[0]
            
            # Get pending requests count
            cursor.execute('SELECT COUNT(*) FROM blood_requests WHERE status = "Pending"')
            pending_requests = cursor.fetchone()[0]
            
            # Get count of unique centers/hospitals
            cursor.execute('SELECT COUNT(DISTINCT hospital_name) FROM users WHERE hospital_name IS NOT NULL')
            center_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Update dashboard statistics
            stats_data = {
                "donor_count": donor_count,
                "blood_units": f"{blood_units}ML",
                "pending_requests": pending_requests,
                "center_count": center_count
            }
            
            # Find and update the stat labels
            for child in self.dashboard_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for stat_frame in child.winfo_children():
                        if isinstance(stat_frame, ttk.LabelFrame):
                            stat_name = stat_frame.cget("text")
                            stat_id = None
                            
                            if stat_name == "Total Donors":
                                stat_id = "donor_count"
                            elif stat_name == "Available Blood Units":
                                stat_id = "blood_units"
                            elif stat_name == "Pending Requests":
                                stat_id = "pending_requests"
                            elif stat_name == "Centers":
                                stat_id = "center_count"
                            
                            if stat_id:
                                for widget in stat_frame.winfo_children():
                                    if isinstance(widget, ttk.Label):
                                        widget.config(text=stats_data[stat_id])
                                        break
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch dashboard data: {str(e)}")

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
            cursor.execute('SELECT DISTINCT hospital_name, email FROM users WHERE hospital_name IS NOT NULL ORDER BY hospital_name')
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
            cursor.execute('SELECT request_id, patient_name, blood_group, quantity_ml, hospital, status, created_at FROM blood_requests')
            requests_data = cursor.fetchall()
            conn.close()
            
            for req in requests_data:
                rowid = req[0]
                values = req[1:] 
                self.request_tree.insert('', 'end', text=str(rowid), values=values)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch request list: {str(e)}")
    
    
    def on_request_select(self, event):
        approve_frame.on_request_select(self, event)

    def approve_request(self):
        approve_frame.approve_request(self)

    def reject_request(self):
        approve_frame.reject_request(self)

    def find_compatible_donors(self, blood_type, quantity_needed):
        approve_frame.find_compatible_donors(self, blood_type, quantity_needed)

