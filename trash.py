class BloodBankApp:
    def __init__(self, parent, username, role, hospital_name=None):
        self.parent = parent
        self.username = username
        self.role = role
        self.hospital_name = hospital_name
        self.API_BASE_URL = "http://localhost:8000"
        
        self.setup_ui()

    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        if self.role == "admin":
            self.setup_admin_view()
        elif self.role == "hospital":
            self.setup_hospital_view()

    def setup_admin_view(self):
        # Create admin tabs
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

    def setup_hospital_view(self):
        # Create hospital tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.donor_reg_frame = ttk.Frame(self.notebook)
        self.requests_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.donor_reg_frame, text="Register Donor")
        self.notebook.add(self.requests_frame, text="Blood Requests")
        
        bb_app.setup_transfusion_center()
        bb_app.setup_blood_requests()
        bb_app.register_donor()
        # self.setup_hospital_dashboard()
        # self.setup_donor_registration()
        # self.setup_hospital_requests()

    # Add the rest of the implementation for dashboard, donor management,
    # blood requests, etc. from the original BloodBankApp class...











    def register_donor(self):
        # Get data from entries
        donor_data = {
            'donor_name': self.donor_entries['donor_name'].get(),
            'blood_type': self.donor_entries['blood_type'].get(),
            'phone': self.donor_entries['phone'].get(),
            'email': self.donor_entries['email'].get(),
            'location': self.donor_entries['location'].get(),
        }
        
        # Validate data
        if not all(donor_data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
