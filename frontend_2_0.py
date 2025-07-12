import tkinter as tk
from tkinter import ttk, messagebox
import backend


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.db_conn = db_connection
        self.title("Store Management System")
        self.geometry("960x540")

        # Configure row and column weights for main window to expand container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        # Create a container frame that will hold all our pages
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew") # Use grid to fill window
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (home_page, bill_page, prod_page):
            pg_name = F.__name__
            frame = F(parent = container, controller = self, db_conn = self.db_conn)
            self.frames[pg_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame("home_page")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise() # Bring the desired frame to the front


class home_page(tk.Frame):
    def __init__(self, parent, controller, db_conn):
        tk.Frame.__init__(self, parent, bg="#ecf0f1") # Light gray background
        self.controller = controller
        self.db_conn = db_conn

        lable = tk.Label(self, text='DASHBOARD', font=('Arial', 38, 'bold'), fg="#34495e",bg="#ecf0f1", justify='center')
        lable.pack(pady=20, expand='True')

        s = ttk.Style()
        s.configure('My.TButton', font= ('Arial', 26, 'bold'), background="#34495e")

        bill_button = ttk.Button(self, text='BILLING', style='My.TButton', command=lambda: controller.show_frame("bill_page"))
        bill_button.pack(pady=0, expand=True)

        product_button = ttk.Button(self, text='PRODUCT', style='My.TButton', command=lambda: controller.show_frame("prod_page"))
        product_button.pack(pady=10, expand=True)

        orders_button = ttk.Button(self, text='ORDERS', style='My.TButton')
        orders_button.pack(pady=0, expand=True)

        analysis_button = ttk.Button(self, text='ANALYSIS', style='My.TButton')
        analysis_button.pack(pady=10, expand=True)

        bottom_bar = tk.Frame(self, bg="#34495e", height=50) # Darker header
        bottom_bar.pack(side="bottom", fill="x", expand=True)



class bill_page(tk.Frame):
    def __init__(self, parent, controller, db_conn):
        tk.Frame.__init__(self, parent, bg="#ecf0f1") # Light gray background
        self.controller = controller
        self.db_conn = db_conn

        # --- Top Bar with Title and Print Button ---
        top_bar = tk.Frame(self, bg="#34495e", height=50) # Darker header
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False) # Prevent frame from shrinking to content

        self.back_button_img = tk.PhotoImage(file="icons8-back-arrow-16.png")
        back_button = tk.Button(top_bar, image=self.back_button_img, command=lambda: controller.show_frame("home_page"), relief='flat', bg="#34495e", activebackground="#425c76")
        back_button.pack(side="left", padx=10)

        title_label = tk.Label(top_bar, text="Billing", font=("Arial", 20, "bold"), fg="white", bg="#34495e")
        title_label.pack(side="left", padx=10)

        print_button = ttk.Button(top_bar, text="Print", command=self.print_bill)
        print_button.pack(side="right", padx=20)

        # --- Data Entry Fields (Above the table) ---
        entry_frame = ttk.LabelFrame(self, text="Item Details", padding=(10, 10))
        entry_frame.pack(pady=10, padx=20, fill="x")

        # Column names for the entry fields
        self.entry_fields = {}
        column_names = ["Product ID", "Product Name", "", "Quantity", ""]
        self.product_suggestions = backend.suggest_prod(self.db_conn) # Pre-existing list

        for i, col_name in enumerate(column_names):
            ttk.Label(entry_frame, text=col_name).grid(row=0, column=i, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(entry_frame)
            if i!=2 and i!=4:
                entry.grid(row=1, column=i, padx=5, pady=5, sticky="ew")
                self.entry_fields[col_name] = entry

            # Special handling for "Product Name" for suggestions
            if col_name == "Product Name":
                self.product_name_entry = entry
                self.product_name_entry.bind("<KeyRelease>", self.on_key_release_product)
                self.suggestion_listbox = tk.Listbox(entry_frame, height=5, selectmode=tk.SINGLE, exportselection=False)
                self.suggestion_listbox.grid(row=2, column=i, columnspan=2, sticky="ew", padx=5, pady=0)
                self.suggestion_listbox.bind("<<ListboxSelect>>", self.select_suggestion)
                self.suggestion_listbox.grid_remove() # Hide initially

            # Special handling for "Quantity" and "MRP" for validation/calculation
            if col_name == "Quantity":
                entry.bind("<FocusOut>", self.calculate_row_total)
                entry.bind("<Return>", self.calculate_row_total)


        # Configure column weights for entry_frame
        for i in range(len(column_names)):
            entry_frame.grid_columnconfigure(i, weight=1)

        # Add/Update Buttons
        button_row_frame = tk.Frame(entry_frame)
        button_row_frame.grid(row=3, column=0, columnspan=len(column_names), pady=10)

        ttk.Button(entry_frame, text="Add New Item", command=self.add_item_to_table).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Button(entry_frame, text="Update Quantity", command=self.update_quantity).grid(row=1, column=4, padx=5, pady=5, sticky="w")
        # ttk.Button(button_row_frame, text="Delete Selected Item", command=self.delete_selected_item).pack(side="left", padx=5)


        # --- Tabular Interface (Treeview) ---
        table_frame = tk.Frame(self)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Define columns
        columns = ("product_id", "product_name", "quantity", "mrp", "rate", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Define column headings and widths
        # self.tree.heading("product_id", text="Product ID")
        self.tree.heading("product_id", text="Product ID")
        self.tree.heading("product_name", text="Product Name")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("mrp", text="MRP")
        self.tree.heading("rate", text="Rate")
        self.tree.heading("total", text="Total")


        # Set column widths (you can adjust these)
        # self.tree.column("product_id", width=80, anchor="center")
        self.tree.column("product_id", width=80, anchor="center")
        self.tree.column("product_name", width=200, anchor="center")
        self.tree.column("quantity", width=80, anchor="center")
        self.tree.column("mrp", width=100, anchor="center")
        self.tree.column("rate", width=100, anchor="center")
        self.tree.column("total", width=120, anchor="center")
        

        # Vertical Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Bind selection event to populate entry fields
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Back Button ---
        delete_button = ttk.Button(self, text="Delete Selected Item", command=self.delete_selected_item)
        delete_button.pack(pady=10)

        self.load_sample_data() # Load some initial data

    def load_sample_data(self):
        """Loads some initial data into the table."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # sample_data = [
        #     (101, "Laptop", 1, 85000.00, 85000.00),
        #     (102, "Mouse", 2, 750.50, 1501.00),
        #     (103, "Keyboard", 1, 1200.00, 1200.00),
        #     (104, "Monitor", 1, 15000.00, 15000.00),
        #     (105, "USB Drive", 5, 300.00, 1500.00),
        # ]
        sample_data = backend.print_table(self.db_conn, 'billing')
        for item in sample_data:
            self.tree.insert("", tk.END, values=item)

    def print_bill(self):
        """Placeholder for print functionality."""
        messagebox.showinfo("Print Bill", "Printing bill... (This is a placeholder)")
        # In a real app, you would generate a report/PDF here.

    def calculate_row_total(self, event=None):
        """Calculates and updates the total field for a row."""
        try:
            qty_str = self.entry_fields["Quantity"].get()
            price_str = self.entry_fields["MRP"].get()

            quantity = float(qty_str) if qty_str else 0
            mrp = float(price_str) if price_str else 0

            total = quantity * mrp
            self.entry_fields["Total"].set(f"{total:.2f}") # Format to 2 decimal places
        except ValueError:
            self.entry_fields["Total"].set("") # Clear if input is invalid

    def add_item_to_table(self):
        """Adds a new item to the Treeview from entry fields."""
        try:
            prod_id = self.entry_fields["Product ID"].get()
            prod_name = self.entry_fields["Product Name"].get()
            # qty = self.entry_fields["Quantity"].get()

            if not any([prod_id, prod_name]):
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return

            # Basic type conversion/validation
            # prod_id = int(prod_id)
            # qty = int(qty)
            # mrp = float(mrp)
            # total = float(total)
            # print("hello")

            # val = backend.fetch_prod(self.db_conn, prod_id)
            # for item in val:
            #     self.tree.insert("", tk.END, values=item)
            if prod_id:
                backend.add_to_bill(self.db_conn, prod_id=prod_id)
            else:
                backend.add_to_bill(self.db_conn, prod_name= prod_name)
            self.clear_entry_fields()
            self.load_sample_data()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for ID, Quantity, Price, and Total.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def update_quantity(self):
        """Updates the selected item in the Treeview with values from entry fields."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection", "Please select an item to update.")
            return

        try:
            values = self.tree.item(selected_item, 'values')
            prod_id = values[0]
            # prod_id = self.entry_fields["Product ID"].get()
            # prod_name = self.entry_fields["Product Name"].get()
            qty = self.entry_fields["Quantity"].get()
            # mrp = self.entry_fields["MRP"].get()
            # total = self.entry_fields["Total"].get()
            print(type(qty))

            if int(qty) is 0:
                self.delete_selected_item()
                return

            if not all([prod_id, qty]):
                messagebox.showwarning("Input Error", "Please fill all fields for update.")
                return

            # Basic type conversion/validation
            prod_id = int(prod_id)
            qty = int(qty)
            # mrp = float(mrp)
            # total = float(total)
            backend.update_quantity(self.db_conn, 'billing', prod_id, qty)
            self.load_sample_data()

            # self.tree.item(selected_item, values=(prod_id, prod_name, qty, mrp, total))
            self.clear_entry_fields()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for ID, Quantity, Price, and Total.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def delete_selected_item(self):
        """Deletes the selected item from the Treeview."""
        selected_item = self.tree.focus()
        print(selected_item)
        if not selected_item:
            messagebox.showwarning("Selection", "Please select an item to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected item?"):
            # self.tree.delete(selected_item)
            values = self.tree.item(selected_item, 'values')
            backend.remove_product(self.db_conn, 'billing', int(values[0]))
            self.load_sample_data()
            self.clear_entry_fields()

    def clear_entry_fields(self):
        """Clears all entry fields."""
        for entry in self.entry_fields.values():
            entry.delete(0, tk.END)

    def on_tree_select(self, event):
        """Populates entry fields when a row in the Treeview is selected."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.entry_fields["Product ID"].set(values[0])
            # self.entry_fields["Product Name"].set(values[1])
            self.entry_fields["Quantity"].set(values[2])
            # self.entry_fields["MRP"].set(values[3])
            # self.entry_fields["Total"].set(values[4])
        else:
            self.clear_entry_fields()

    def on_key_release_product(self, event):
        """Handles key release event for product name entry to show suggestions."""
        current_text = self.product_name_entry.get().lower()
        if current_text:
            matching_suggestions = [
                s for s in self.product_suggestions if current_text in s.lower()
            ]
            self.update_suggestion_listbox(matching_suggestions)
        else:
            self.suggestion_listbox.grid_remove() # Hide listbox if entry is empty

    def update_suggestion_listbox(self, suggestions):
        """Updates the suggestion listbox with filtered items."""
        self.suggestion_listbox.delete(0, tk.END)
        if suggestions:
            for s in suggestions:
                self.suggestion_listbox.insert(tk.END, s)
            self.suggestion_listbox.grid() # Show listbox
        else:
            self.suggestion_listbox.grid_remove() # Hide if no matches

    def select_suggestion(self, event):
        """Selects an item from the suggestion listbox and puts it into the entry."""
        if self.suggestion_listbox.curselection():
            selected_index = self.suggestion_listbox.curselection()[0]
            selected_value = self.suggestion_listbox.get(selected_index)
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, selected_value)
            self.suggestion_listbox.grid_remove() # Hide listbox after selection




class prod_page(tk.Frame):
    def __init__(self, parent, controller, db_conn):
        tk.Frame.__init__(self, parent, bg="#ecf0f1") # Light gray background
        self.controller = controller
        self.db_conn = db_conn

        # --- Top Bar with Title and Print Button ---
        top_bar = tk.Frame(self, bg="#34495e", height=50) # Darker header
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False) # Prevent frame from shrinking to content

        self.back_button_img = tk.PhotoImage(file="icons8-back-arrow-16.png")
        back_button = tk.Button(top_bar, image=self.back_button_img, command=lambda: controller.show_frame("home_page"), relief='flat', bg="#34495e", activebackground="#425c76")
        back_button.pack(side="left", padx=10)

        title_label = tk.Label(top_bar, text="Products", font=("Arial", 20, "bold"), fg="white", bg="#34495e")
        title_label.pack(side="left", padx=10)

        print_button = ttk.Button(top_bar, text="Print")
        print_button.pack(side="right", padx=20)


        ## buttons 
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(side=tk.TOP, fill=tk.X)

        add_button = ttk.Button(button_frame, text="Add Product", command=self.add_product_dialog)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text="Edit Product", command=self.edit_product_dialog)
        edit_button.pack(side=tk.LEFT, padx=5)


    

    def add_product_dialog(self):
        self.open_product_dialog("Add New Product")


    

    def edit_product_dialog(self):
        self.open_product_dialog("Edit Product")

    


    def open_product_dialog(self, title, initial_data = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()


        self.entry_fields = {}
        column_names = ["Product ID", "Product Name", "Quantity", "MRP", "Discount"]
        self.product_suggestions = backend.suggest_prod(self.db_conn) # Pre-existing list


        for i, col_name in enumerate(column_names):
            ttk.Label(dialog, text=col_name).grid(row=2*i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=2*i, column=1, padx=5, pady=5, sticky="ew")
            self.entry_fields[col_name] = entry

            if col_name == "Product Name":
                self.product_name_entry = entry
                self.product_name_entry.bind("<KeyRelease>", self.on_key_release_product)
                self.suggestion_listbox = tk.Listbox(dialog, height=5, selectmode=tk.SINGLE, exportselection=False)
                self.suggestion_listbox.grid(row=2*i+1, column=1, columnspan=1, sticky="ew", padx=0, pady=0)
                self.suggestion_listbox.bind("<<ListboxSelect>>", self.select_suggestion)
                self.suggestion_listbox.grid_remove() # Hide initially




    def on_key_release_product(self, event):
        """Handles key release event for product name entry to show suggestions."""
        current_text = self.product_name_entry.get().lower()
        if current_text:
            matching_suggestions = [
                s for s in self.product_suggestions if current_text in s.lower()
            ]
            self.update_suggestion_listbox(matching_suggestions)
        else:
            self.suggestion_listbox.grid_remove() # Hide listbox if entry is empty



    def update_suggestion_listbox(self, suggestions):
        """Updates the suggestion listbox with filtered items."""
        self.suggestion_listbox.delete(0, tk.END)
        if suggestions:
            for s in suggestions:
                self.suggestion_listbox.insert(tk.END, s)
            self.suggestion_listbox.grid() # Show listbox
        else:
            self.suggestion_listbox.grid_remove() # Hide if no matches

    def select_suggestion(self, event):
        """Selects an item from the suggestion listbox and puts it into the entry."""
        if self.suggestion_listbox.curselection():
            selected_index = self.suggestion_listbox.curselection()[0]
            selected_value = self.suggestion_listbox.get(selected_index)
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, selected_value)
            self.suggestion_listbox.grid_remove() # Hide listbox after selection




if __name__ == "__main__":
    db_connection = backend.connect_db()
    app = App()
    app.protocol("WM_DELETE_WINDOW", lambda: [backend.close_db(db_connection), app.destroy()]) # Ensure connection closes on app exit
    app.mainloop()