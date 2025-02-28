from tkinter import ttk, messagebox
import sqlite3

def setup_request_approval(self):
    # Create approval frame as a child of requests_frame
    self.approval_frame = ttk.LabelFrame(self.requests_frame, text="Approve Blood Request")
    self.approval_frame.pack(padx=20, pady=10, fill='x')
    
    # Add selection feature to the request treeview - FIXED EVENT BINDING
    self.request_tree.bind("<<TreeviewSelect>>", self.on_request_select)
    
    # Request details section
    details_frame = ttk.Frame(self.approval_frame)
    details_frame.pack(fill='x', padx=10, pady=10)
    
    # Left side - Request details
    left_frame = ttk.Frame(details_frame)
    left_frame.pack(side='left', fill='y', padx=10)
    
    ttk.Label(left_frame, text="Patient:").grid(row=0, column=0, sticky='w', pady=2)
    self.patient_var = ttk.Label(left_frame, text="-")
    self.patient_var.grid(row=0, column=1, sticky='w', pady=2, padx=5)
    
    ttk.Label(left_frame, text="Blood Type:").grid(row=1, column=0, sticky='w', pady=2)
    self.blood_type_var = ttk.Label(left_frame, text="-")
    self.blood_type_var.grid(row=1, column=1, sticky='w', pady=2, padx=5)
    
    ttk.Label(left_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=2)
    self.quantity_var = ttk.Label(left_frame, text="-")
    self.quantity_var.grid(row=2, column=1, sticky='w', pady=2, padx=5)
    
    ttk.Label(left_frame, text="Hospital:").grid(row=3, column=0, sticky='w', pady=2)
    self.hospital_var = ttk.Label(left_frame, text="-")
    self.hospital_var.grid(row=3, column=1, sticky='w', pady=2, padx=5)
    
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
    
    # Button frame
    button_frame = ttk.Frame(self.approval_frame)
    button_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Button(button_frame, text="Approve Request", 
              command=self.approve_request).pack(side='right', padx=5)
    ttk.Button(button_frame, text="Reject Request", 
              command=self.reject_request).pack(side='right', padx=5)

def on_request_select(self, event):
    # Get selected item
    selection = self.request_tree.selection()
    if not selection:
        return
    
    # Get the request_id from the 'text' attribute
    self.selected_request_id = self.request_tree.item(selection[0], 'text')
    
    # Get values from the selected request
    item = self.request_tree.item(selection[0])
    values = item['values']
    
    # Populate request details
    self.patient_var.config(text=values[0])  # Patient name
    self.blood_type_var.config(text=values[1])  # Blood type
    self.quantity_var.config(text=f"{values[2]} ml")  # Quantity
    self.hospital_var.config(text=values[3])  # Hospital
    
    # Find compatible donors
    self.find_compatible_donors(values[1], values[2])

    
def find_compatible_donors(self, blood_type, quantity_needed):
    # Clear existing items
    for item in self.donor_select_tree.get_children():
        self.donor_select_tree.delete(item)
    
    # Blood type compatibility chart
    compatibility = {
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'AB-': ['A-', 'B-', 'AB-', 'O-'],
        'O+': ['O+', 'O-'],
        'O-': ['O-']
    }
    
    compatible_types = compatibility.get(blood_type, [])
    
    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        
        # Format list of compatible types for SQL query
        types_str = ', '.join([f"'{t}'" for t in compatible_types])
        
        # Get compatible donors with sufficient quantity
        query = f"""
        SELECT hospital, donor_name, blood_type, quantity_ml 
        FROM donors 
        WHERE blood_type IN ({types_str}) AND quantity_ml >= ?
        ORDER BY 
            CASE 
                WHEN blood_type = ? THEN 0  
                ELSE 1
            END,
            quantity_ml DESC
        """
        
        cursor.execute(query, (quantity_needed, blood_type))
        donors = cursor.fetchall()
        
        # Insert compatible donors into treeview
        for i, donor in enumerate(donors):
            # Insert with a unique ID that we can reference later
            self.donor_select_tree.insert('', 'end', iid=f"donor_{i}", values=donor)
            
        conn.close()
        
        if not donors:
            messagebox.showinfo("No Matches", "No compatible donors with sufficient quantity found.")
            
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to find compatible donors: {str(e)}")

def approve_request(self):
    selection = self.donor_select_tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a blood provider")
        return
    
    if not hasattr(self, 'selected_request_id') or not self.selected_request_id:
        messagebox.showwarning("Warning", "Please select a request first")
        return
    
    # Get donor details
    donor_item = self.donor_select_tree.item(selection[0])
    donor_values = donor_item['values']
    donor_hospital = donor_values[0]
    donor_name = donor_values[1]
    donor_blood_type = donor_values[2]
    donor_available = int(donor_values[3])  # Available quantity
    
    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        
        # Get the requested quantity and other details
        cursor.execute("""
            SELECT quantity_ml, patient_name, blood_group, hospital 
            FROM blood_requests 
            WHERE request_id = ?
        """, (self.selected_request_id,))
        
        request_data = cursor.fetchone()
        if not request_data:
            messagebox.showerror("Error", "Request not found in database")
            conn.close()
            return
            
        requested_quantity = int(request_data[0])
        patient_name = request_data[1]
        blood_group = request_data[2]
        requesting_hospital = request_data[3]
        
        # Check if partial fulfillment is needed
        if donor_available < requested_quantity:
            result = messagebox.askyesno(
                "Partial Fulfillment", 
                f"The selected donor only has {donor_available}ml available, but {requested_quantity}ml was requested.\n\n"
                f"Would you like to partially fulfill this request and create a new request for the remaining amount?"
            )
            
            if not result:
                conn.close()
                return
                
            # Partial fulfillment - Split the request
            remaining_quantity = requested_quantity - donor_available
            fulfilled_quantity = donor_available
            
            # Update the existing request to be partially fulfilled
            cursor.execute(
                """UPDATE blood_requests 
                   SET status = 'Partially Approved', 
                       quantity_ml = ?,
                       hospital = ?, 
                       donor = ?,
                       approved_at = CURRENT_TIMESTAMP,
                       notes = 'Partially fulfilled'
                   WHERE request_id = ?""", 
                (fulfilled_quantity, donor_hospital, donor_name, self.selected_request_id)
            )
            
            # Create a new request for the remaining quantity
            cursor.execute(
                """INSERT INTO blood_requests 
                   (patient_name, blood_group, quantity_ml, hospital, status, created_at, notes) 
                   VALUES (?, ?, ?, ?, 'Pending', CURRENT_TIMESTAMP, 'Remaining from partial approval')""",
                (patient_name, blood_group, remaining_quantity, requesting_hospital)
            )
            
            message = f"Request partially approved for {fulfilled_quantity}ml. Remaining {remaining_quantity}ml marked as pending."
            
        else:
            # Full approval
            cursor.execute(
                """UPDATE blood_requests 
                   SET status = 'Approved', 
                       hospital = ?, 
                       donor = ?,
                       approved_at = CURRENT_TIMESTAMP
                   WHERE request_id = ?""", 
                (donor_hospital, donor_name, self.selected_request_id)
            )
            fulfilled_quantity = requested_quantity
            message = "Blood request approved successfully"
        
        # Update donor's available quantity
        cursor.execute(
            """UPDATE donors 
               SET quantity_ml = quantity_ml - ?
               WHERE donor_name = ? AND hospital = ?""",
            (fulfilled_quantity, donor_name, donor_hospital)
        )
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", message)
        
        # Refresh lists
        self.refresh_request_list()
        self.refresh_donor_list()
        self.refresh_dashboard()
        
        # Clear selection
        self.patient_var.config(text="-")
        self.blood_type_var.config(text="-")
        self.quantity_var.config(text="-")
        self.hospital_var.config(text="-")
        
        for item in self.donor_select_tree.get_children():
            self.donor_select_tree.delete(item)
            
        # Clear the selected request ID
        self.selected_request_id = None
            
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to approve request: {str(e)}")

def reject_request(self):
    if not hasattr(self, 'selected_request_id') or not self.selected_request_id:
        messagebox.showwarning("Warning", "Please select a request first")
        return
    
    if messagebox.askyesno("Confirm", "Are you sure you want to reject this request?"):
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            
            # Update request status
            cursor.execute(
                """UPDATE blood_requests 
                   SET status = 'Rejected', 
                       rejected_at = CURRENT_TIMESTAMP,
                       notes = 'Rejected by administrator'
                   WHERE request_id = ?""", 
                (self.selected_request_id,)
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Blood request rejected")
            
            # Refresh requests list
            self.refresh_request_list()
            self.refresh_dashboard()
            
            # Clear selection
            self.patient_var.config(text="-")
            self.blood_type_var.config(text="-")
            self.quantity_var.config(text="-")
            self.hospital_var.config(text="-")
            
            for item in self.donor_select_tree.get_children():
                self.donor_select_tree.delete(item)
                
            # Clear the selected request ID
            self.selected_request_id = None
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to reject request: {str(e)}")