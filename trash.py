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
