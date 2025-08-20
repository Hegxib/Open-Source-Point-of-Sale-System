import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import POSDatabase
import csv

class InventoryManager:
    def __init__(self, parent):
        self.parent = parent
        self.db = POSDatabase()
        self.window = None
        self.zoom_level = 1.0
        
    def open_inventory_window(self):
        """Open inventory management window"""
        if self.window and self.window.winfo_exists():
            self.window.focus()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Inventory Management")
        self.window.geometry("900x550")
        self.window.configure(bg='#f8f9fa')
        
        # Bind zoom controls
        self.window.bind("<Control-MouseWheel>", self.handle_zoom)
        self.window.bind("<Control-Button-4>", lambda e: self.zoom_in())
        self.window.bind("<Control-Button-5>", lambda e: self.zoom_out())
        
        self.setup_styles()
        
        # Compact grid layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Minimal header
        header_frame = tk.Frame(self.window, bg='#ffffff', height=35)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        header_frame.grid_propagate(False)
        
        tk.Label(header_frame, text="Inventory Management", 
                font=("Segoe UI", int(12 * self.zoom_level)), fg='#495057', bg='#ffffff').pack(pady=8)
        
        # Left panel - actions
        self.create_compact_actions(self.window)
        
        # Right panel - products
        self.create_compact_products(self.window)
        
        self.refresh_list()
    
    def setup_styles(self):
        """Configure compact, flat styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Compact button styles
        style.configure("Compact.TButton",
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       padding=(8, 4),
                       background='#007bff',
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        
        style.map("Compact.TButton",
                 background=[('active', '#0056b3')])
        
        style.configure("Danger.TButton",
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       padding=(8, 4),
                       background='#dc3545',
                       foreground='white',
                       borderwidth=0)
        
        # Minimal treeview
        style.configure("Compact.Treeview",
                       background='#ffffff',
                       foreground='#495057',
                       fieldbackground='#ffffff',
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       rowheight=int(22 * self.zoom_level),
                       borderwidth=0)
        
        style.configure("Compact.Treeview.Heading",
                       background='#e9ecef',
                       foreground='#495057',
                       font=("Segoe UI", int(9 * self.zoom_level), "bold"),
                       padding=(4, 2))
    
    def create_compact_actions(self, parent):
        """Create compact action panel"""
        action_frame = tk.Frame(parent, bg='#ffffff', width=150)
        action_frame.grid(row=1, column=0, sticky="ns", padx=(8, 4), pady=(0, 8))
        action_frame.grid_propagate(False)
        
        # Search section
        search_frame = tk.Frame(action_frame, bg='#ffffff')
        search_frame.pack(fill="x", padx=6, pady=(8, 12))
        
        tk.Label(search_frame, text="Search:", 
                font=("Segoe UI", int(9 * self.zoom_level)), fg='#495057', bg='#ffffff').pack(anchor="w")
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame,
                                   textvariable=self.search_var,
                                   font=("Segoe UI", int(9 * self.zoom_level)),
                                   bg='#f8f9fa', fg='#495057',
                                   relief='solid', bd=1)
        self.search_entry.pack(fill="x", pady=(2, 0))
        self.search_var.trace('w', self.filter_products)
        
        # Zoom controls
        zoom_frame = tk.Frame(action_frame, bg='#ffffff')
        zoom_frame.pack(fill="x", padx=6, pady=(0, 8))
        
        tk.Label(zoom_frame, text="Zoom:", 
                font=("Segoe UI", int(8 * self.zoom_level)), fg='#6c757d', bg='#ffffff').pack(anchor="w")
        
        zoom_controls = tk.Frame(zoom_frame, bg='#ffffff')
        zoom_controls.pack(fill="x")
        
        tk.Button(zoom_controls, text="-", command=self.zoom_out,
                 font=("Segoe UI", int(8 * self.zoom_level)), bg='#6c757d', fg='white',
                 width=2, relief='flat', bd=0).pack(side="left")
        
        tk.Button(zoom_controls, text="+", command=self.zoom_in,
                 font=("Segoe UI", int(8 * self.zoom_level)), bg='#6c757d', fg='white',
                 width=2, relief='flat', bd=0).pack(side="right")
        
        # Action buttons
        separator = tk.Frame(action_frame, bg='#dee2e6', height=1)
        separator.pack(fill="x", padx=6, pady=4)
        
        ttk.Button(action_frame, text="Add", command=self.add_product, 
                  style="Compact.TButton").pack(fill="x", padx=6, pady=2)
        
        ttk.Button(action_frame, text="Edit", command=self.edit_product,
                  style="Compact.TButton").pack(fill="x", padx=6, pady=2)
        
        ttk.Button(action_frame, text="Delete", command=self.delete_product,
                  style="Danger.TButton").pack(fill="x", padx=6, pady=2)
        
        ttk.Button(action_frame, text="Export", command=self.export_csv,
                  style="Compact.TButton").pack(fill="x", padx=6, pady=2)
        
        ttk.Button(action_frame, text="Refresh", command=self.refresh_list,
                  style="Compact.TButton").pack(fill="x", padx=6, pady=2)
    
    def create_compact_products(self, parent):
        """Create compact products display"""
        products_frame = tk.Frame(parent, bg='#ffffff')
        products_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        products_frame.grid_columnconfigure(0, weight=1)
        products_frame.grid_rowconfigure(0, weight=1)
        
        # Compact treeview
        self.tree = ttk.Treeview(products_frame,
                                columns=("ID", "Barcode", "Name", "Price", "Stock"),
                                show="headings",
                                style="Compact.Treeview")
        
        # Compact headers
        self.tree.heading("ID", text="ID")
        self.tree.heading("Barcode", text="Barcode")
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Stock", text="Stock")
        
        # Optimized column widths
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Barcode", width=100, anchor="center")
        self.tree.column("Name", width=220, anchor="w")
        self.tree.column("Price", width=70, anchor="center")
        self.tree.column("Stock", width=60, anchor="center")
        
        # Minimal scrollbar
        scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Row styling
        self.tree.tag_configure('low_stock', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('normal', background='#ffffff', foreground='#495057')
        
        self.tree.bind("<Double-1>", lambda e: self.edit_product())
    
    def filter_products(self, *args):
        """Filter products based on search term"""
        search_term = self.search_var.get().lower()
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = self.db.get_all_products()
        
        for product in products:
            # Check if search term matches product name or barcode
            if (search_term in product[2].lower() or 
                search_term in product[1].lower() or
                not search_term):
                
                tag = 'low_stock' if product[4] < 5 else 'normal'
                
                self.tree.insert("", "end",
                               values=(product[0], product[1], product[2],
                                      f"{product[3]:.2f} DA", product[4]),
                               tags=(tag,))
    
    def handle_zoom(self, event):
        """Handle mouse wheel zoom with Ctrl"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 1.5:
            self.zoom_level += 0.1
            self.refresh_zoom()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.7:
            self.zoom_level -= 0.1
            self.refresh_zoom()
    
    def refresh_zoom(self):
        """Refresh UI with new zoom level"""
        self.setup_styles()
        # Force redraw of treeview
        self.tree.configure(style="Compact.Treeview")
    
    def refresh_list(self):
        """Refresh product list"""
        self.filter_products()

    def add_product(self):
        """Add new product dialog"""
        dialog = ProductDialog(self.window, "Add Product")
        if dialog.result:
            barcode, name, price, stock = dialog.result
            if self.db.add_product(barcode, name, price, stock):
                self.refresh_list()
                messagebox.showinfo("Success", "Product added successfully!")
            else:
                messagebox.showerror("Error", "Product with this barcode already exists!")
    
    def edit_product(self):
        """Edit selected product"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
        
        item = self.tree.item(selection[0])
        product_id = item['values'][0]
        current_name = item['values'][2]
        current_price = float(item['values'][3].replace(' DA', ''))
        current_stock = int(item['values'][4])
        
        dialog = ProductDialog(self.window, "Edit Product", 
                             current_name, current_price, current_stock)
        if dialog.result:
            _, name, price, stock = dialog.result
            self.db.update_product(product_id, name, price, stock)
            self.refresh_list()
            messagebox.showinfo("Success", "Product updated successfully!")
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            item = self.tree.item(selection[0])
            product_id = item['values'][0]
            self.db.delete_product(product_id)
            self.refresh_list()
            messagebox.showinfo("Success", "Product deleted successfully!")
    
    def export_csv(self):
        """Export products to CSV"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            products = self.db.get_all_products()
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Barcode", "Name", "Price", "Stock"])
                writer.writerows(products)
            messagebox.showinfo("Success", f"Products exported to {filename}")

class ProductDialog:
    def __init__(self, parent, title, name="", price=0.0, stock=0):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x380")
        self.dialog.configure(bg='#f8f9fa')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Compact layout
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Minimal title
        tk.Label(self.dialog, text=title,
                font=("Segoe UI", 12), fg='#495057', bg='#f8f9fa').grid(row=0, column=0, pady=(12, 16))
        
        # Compact form
        form_frame = tk.Frame(self.dialog, bg='#ffffff', relief='solid', bd=1)
        form_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Form fields
        self.create_compact_field(form_frame, "Barcode:", 0)
        self.barcode_entry = self.create_compact_entry(form_frame, 1)
        
        self.create_compact_field(form_frame, "Product Name:", 2)
        self.name_entry = self.create_compact_entry(form_frame, 3, name)
        
        self.create_compact_field(form_frame, "Price (DA):", 4)
        self.price_entry = self.create_compact_entry(form_frame, 5, str(price))
        
        self.create_compact_field(form_frame, "Stock:", 6)
        self.stock_entry = self.create_compact_entry(form_frame, 7, str(stock))
        
        # Compact buttons
        button_frame = tk.Frame(self.dialog, bg='#f8f9fa')
        button_frame.grid(row=2, column=0, pady=12)
        
        tk.Button(button_frame, text="Confirm", command=self.ok_clicked,
                 font=("Segoe UI", 9), bg='#007bff', fg='white',
                 padx=16, pady=6, relief='flat', bd=0).pack(side="left", padx=4)
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 font=("Segoe UI", 9), bg='#6c757d', fg='white',
                 padx=16, pady=6, relief='flat', bd=0).pack(side="left", padx=4)
        
        self.barcode_entry.focus_set()
        self.dialog.wait_window()
    
    def create_compact_field(self, parent, text, row):
        """Create compact form field label"""
        label = tk.Label(parent, text=text,
                        font=("Segoe UI", 9), fg='#495057', bg='#ffffff',
                        anchor="w")
        label.grid(row=row, column=0, sticky="w", pady=(8, 2), padx=12)
    
    def create_compact_entry(self, parent, row, value=""):
        """Create compact entry field"""
        entry = tk.Entry(parent,
                        font=("Segoe UI", 9), width=25,
                        bg='#f8f9fa', fg='#495057',
                        relief='solid', bd=1)
        entry.grid(row=row, column=0, sticky="ew", pady=(0, 8), padx=12)
        entry.insert(0, value)
        return entry
    
    def ok_clicked(self):
        try:
            barcode = self.barcode_entry.get().strip()
            name = self.name_entry.get().strip()
            price = float(self.price_entry.get())
            stock = int(self.stock_entry.get())
            
            if not barcode or not name:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            if price < 0 or stock < 0:
                messagebox.showerror("Error", "Price and stock must be positive values.")
                return
            
            self.result = (barcode, name, price, stock)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and stock values.")
