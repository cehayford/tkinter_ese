import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


def show_edit_donor_form(self):
    # Create a new top-level window for editing
    edit_window = tk.Toplevel(self.root)
    edit_window.title("Edit Donor")
    edit_window.geometry("500x500")
    edit_window.grab_set()  # Make window modal
    
    # Create a frame with padding
    frame = ttk.Frame(edit_window, padding="20")
    frame.pack(fill='both', expand=True)
    
    # Header
    ttk.Label(frame, text="Edit Donor Information", font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Donor ID (hidden)
    selected_item = self.donor_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a donor to edit", parent=edit_window)
        edit_window.destroy()
        return
    donor_data = self.donor_tree.item(selected_item)['values']
    donor_id = donor_data[5]
    
    # Create form fields
    fields = [
        ("Donor Name:", "donor_name", ttk.Entry, donor_data[0]),
        ("Blood Type:", "blood_type", ttk.Combobox, donor_data[1]),
        ("Phone:", "phone", ttk.Entry, donor_data[2]),
        ("Email:", "email", ttk.Entry, donor_data[3]),
        ("Location:", "location", ttk.Entry, donor_data[4]),
        ("Quantity (ml):", "quantity_ml", ttk.Entry, "") # This might need to be fetched from the database
    ]
    
    # Dictionary to store entry widgets
    edit_entries = {}
    
    # Create labeled input fields
    for i, (label, field_name, widget, value) in enumerate(fields):
        # Create a frame for each field
        field_frame = ttk.Frame(frame)
        field_frame.pack(fill='x', pady=5)
        
        # Add label
        ttk.Label(field_frame, text=label, width=15).pack(side='left')
        
        # Add entry widget
        if widget == ttk.Combobox:
            edit_entries[field_name] = widget(field_frame, values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
        else:
            edit_entries[field_name] = widget(field_frame, width=30)
        
        edit_entries[field_name].pack(side='left', fill='x', expand=True, padx=5)
        
        # Set current value
        if value:
            if isinstance(edit_entries[field_name], ttk.Combobox):
                edit_entries[field_name].set(value)
            else:
                edit_entries[field_name].insert(0, value)
    
    # Try to fetch additional donor data from database if needed
    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT quantity_ml FROM donors WHERE donor_id = ?', (donor_id,))
        result = cursor.fetchone()
        if result:
            edit_entries['quantity_ml'].insert(0, result[0])
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to fetch complete donor data: {str(e)}")
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    # Save button
    def save_changes():
        # Validation
        if not all(edit_entries[field_name].get() for field_name in edit_entries):
            messagebox.showerror("Error", "All fields are required!", parent=edit_window)
            return
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE donors 
                SET donor_name=?, blood_type=?, phone=?, email=?, location=?, quantity_ml=?
                WHERE donor_id=?
            ''', (
                edit_entries['donor_name'].get(),
                edit_entries['blood_type'].get(),
                edit_entries['phone'].get(),
                edit_entries['email'].get(),
                edit_entries['location'].get(),
                edit_entries['quantity_ml'].get(),
                donor_id
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Donor information updated successfully!", parent=edit_window)
            edit_window.destroy()
            self.refresh_donor_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update donor: {str(e)}", parent=edit_window)
    
    ttk.Button(button_frame, text="Save Changes", command=save_changes, width=15).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, width=15).pack(side='left', padx=5)


def show_edit_request_form(self):
    # Create a new top-level window for editing
    edit_window = tk.Toplevel(self.root)
    edit_window.title("Edit Blood Request")
    edit_window.geometry("500x550")
    edit_window.grab_set()  # Make window modal
    
    # Create a frame with padding
    frame = ttk.Frame(edit_window, padding="20")
    frame.pack(fill='both', expand=True)
    
    # Header
    ttk.Label(frame, text="Edit Blood Request", font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Request ID (hidden)
    selected_item = self.request_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a request to edit", parent=edit_window)
        edit_window.destroy()
        return 
    request_data = self.request_tree.item(selected_item)['values']
    request_id = request_data[6]
    
    # Create form fields
    fields = [
        ("Patient Name:", "patient_name", ttk.Entry, request_data[0]),
        ("Blood Type:", "blood_type", ttk.Combobox, request_data[1]),
        ("Quantity (ml):", "quantity_ml", ttk.Entry, request_data[2]),
        ("Hospital:", "hospital", ttk.Entry, request_data[3]),
        ("Status:", "status", ttk.Combobox, request_data[4]),
        ("Location:", "location", ttk.Entry, "")  # This needs to be fetched from the database
    ]
    
    # Dictionary to store entry widgets
    edit_entries = {}
    
    # Create labeled input fields
    for i, (label, field_name, widget, value) in enumerate(fields):
        # Create a frame for each field
        field_frame = ttk.Frame(frame)
        field_frame.pack(fill='x', pady=5)
        
        # Add label
        ttk.Label(field_frame, text=label, width=15).pack(side='left')
        
        # Add entry widget
        if widget == ttk.Combobox:
            if field_name == "blood_type":
                edit_entries[field_name] = widget(field_frame, values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
            elif field_name == "status":
                edit_entries[field_name] = widget(field_frame, values=['Pending', 'Processing', 'Fulfilled', 'Cancelled'])
            else:
                edit_entries[field_name] = widget(field_frame)
        else:
            edit_entries[field_name] = widget(field_frame, width=30)
        
        edit_entries[field_name].pack(side='left', fill='x', expand=True, padx=5)
        
        # Set current value
        if value:
            if isinstance(edit_entries[field_name], ttk.Combobox):
                edit_entries[field_name].set(value)
            else:
                edit_entries[field_name].insert(0, value)
    
    # Try to fetch additional request data from database if needed
    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT location FROM blood_requests WHERE request_id = ?', (request_id,))
        result = cursor.fetchone()
        if result:
            edit_entries['location'].insert(0, result[0])
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to fetch complete request data: {str(e)}")
    
    # Additional notes field
    notes_frame = ttk.LabelFrame(frame, text="Additional Notes")
    notes_frame.pack(fill='x', pady=10, padx=5)
    
    notes_text = tk.Text(notes_frame, height=4, width=40)
    notes_text.pack(pady=5, padx=5, fill='both', expand=True)
    
    # Try to fetch notes from database
    try:
        conn = sqlite3.connect('bloodbank_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT notes FROM blood_requests WHERE request_id = ?', (request_id,))
        result = cursor.fetchone()
        if result and result[0]:
            notes_text.insert('1.0', result[0])
        conn.close()
    except sqlite3.Error:
        pass  # Just ignore if notes field doesn't exist
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    # Save button
    def save_changes():
        # Validation for required fields
        required_fields = ['patient_name', 'blood_type', 'quantity_ml', 'hospital', 'status']
        if not all(edit_entries[field].get() for field in required_fields):
            messagebox.showerror("Error", "All fields except notes are required!", parent=edit_window)
            return
        
        try:
            conn = sqlite3.connect('bloodbank_users.db')
            cursor = conn.cursor()
            
            # First check if notes column exists, add it if it doesn't
            try:
                cursor.execute("SELECT notes FROM blood_requests LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE blood_requests ADD COLUMN notes TEXT")
            
            # Update the request
            cursor.execute('''
                UPDATE blood_requests 
                SET patient_name=?, blood_group=?, quantity_ml=?, hospital=?, status=?, location=?, notes=?
                WHERE request_id=?
            ''', (
                edit_entries['patient_name'].get(),
                edit_entries['blood_type'].get(),
                edit_entries['quantity_ml'].get(),
                edit_entries['hospital'].get(),
                edit_entries['status'].get(),
                edit_entries['location'].get(),
                notes_text.get('1.0', 'end-1c'),
                request_id
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Blood request updated successfully!", parent=edit_window)
            edit_window.destroy()
            self.refresh_request_list()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update request: {str(e)}", parent=edit_window)
    
    ttk.Button(button_frame, text="Save Changes", command=save_changes, width=15).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, width=15).pack(side='left', padx=5)