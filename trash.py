# Right side - Hospital selection
    right_frame = ttk.Frame(details_frame)
    right_frame.pack(side='right', fill='both', expand=True, padx=10)
    
    ttk.Label(right_frame, text="Select Blood Provider:").pack(anchor='w', pady=2)
    
    # Create treeview for compatible donors
    columns = ('Hospital', 'Donor Name', 'Blood Type', 'Quantity Available')
    self.donor_select_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=5)
    
    for col in columns:
        self.donor_select_tree.heading(col, text=col)
        self.donor_select_tree.column(col, width=100)
    
    self.donor_select_tree.pack(pady=5, fill='x')
    










    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        
        # Update request status
        cursor.execute(
            """UPDATE blood_requests 
               SET status = 'Approved', 
                   provider_hospital = ?, 
                   provider_donor = ?,
                   approved_at = CURRENT_TIMESTAMP
               WHERE rowid = ?""", 
            (donor_hospital, donor_name, self.selected_request_id)
        )
        








        