import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from database import POSDatabase
from inventory_manager import InventoryManager
import datetime
import shutil
import os

class POSSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POS System")
        self.root.geometry("1000x650")
        self.root.configure(bg='#f8f9fa')
        
        self.db = POSDatabase()
        self.inventory_manager = InventoryManager(self.root)
        self.cart = {}
        self.admin_password = "admin123"
        self.last_sale_id = None
        self.zoom_level = 1.0
        
        # Bind zoom controls
        self.root.bind("<Control-MouseWheel>", self.handle_zoom)
        
        self.setup_styles()
        self.setup_ui()
        self.barcode_entry.focus_set()
        self.auto_backup()
    
    def setup_styles(self):
        """Configure compact, modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Compact button styles
        style.configure("Primary.TButton",
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       padding=(10, 5),
                       background='#007bff',
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        
        style.configure("Success.TButton",
                       font=("Segoe UI", int(11 * self.zoom_level), "bold"),
                       padding=(16, 8),
                       background='#28a745',
                       foreground='white',
                       borderwidth=0)
        
        style.configure("Danger.TButton",
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       padding=(8, 4),
                       background='#dc3545',
                       foreground='white',
                       borderwidth=0)
        
        # Compact cart treeview
        style.configure("Cart.Treeview",
                       background='#ffffff',
                       foreground='#495057',
                       fieldbackground='#ffffff',
                       font=("Segoe UI", int(9 * self.zoom_level)),
                       rowheight=int(24 * self.zoom_level),
                       borderwidth=0)
        
        style.configure("Cart.Treeview.Heading",
                       background='#e9ecef',
                       foreground='#495057',
                       font=("Segoe UI", int(9 * self.zoom_level), "bold"),
                       padding=(4, 3))
    
    def setup_ui(self):
        """Setup compact POS interface"""
        # Tight grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Compact scanner section
        self.create_compact_scanner()
        
        # Left panel - actions and total
        self.create_compact_actions()
        
        # Center - cart
        self.create_compact_cart()
        
        # Bottom - checkout
        self.create_compact_checkout()
    
    def create_compact_scanner(self):
        """Create compact scanner section"""
        scanner_frame = tk.Frame(self.root, bg='#ffffff', height=70)
        scanner_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        scanner_frame.grid_propagate(False)
        scanner_frame.grid_columnconfigure(1, weight=1)
        
        # Compact inputs in single row
        tk.Label(scanner_frame, text="Scan/Search:",
                font=("Segoe UI", int(9 * self.zoom_level)), fg='#495057', bg='#ffffff').grid(row=0, column=0, padx=8, sticky="w")
        
        # Combined barcode/product search
        self.search_var = tk.StringVar()
        self.barcode_entry = tk.Entry(scanner_frame,
                                    textvariable=self.search_var,
                                    font=("Segoe UI", int(10 * self.zoom_level)),
                                    bg='#f8f9fa', fg='#495057',
                                    relief='solid', bd=1,
                                    width=30)
        self.barcode_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.barcode_entry.bind("<Return>", self.process_search)
        self.search_var.trace('w', self.show_search_suggestions)
        
        # Quick add button
        tk.Button(scanner_frame, text="Add",
                 command=self.process_search,
                 font=("Segoe UI", int(9 * self.zoom_level)),
                 bg='#007bff', fg='white',
                 padx=12, pady=4, relief='flat', bd=0).grid(row=0, column=2, padx=8)
        
        # Customer field
        tk.Label(scanner_frame, text="Customer:",
                font=("Segoe UI", int(8 * self.zoom_level)), fg='#6c757d', bg='#ffffff').grid(row=1, column=0, padx=8, sticky="w")
        
        self.customer_entry = tk.Entry(scanner_frame,
                                     font=("Segoe UI", int(9 * self.zoom_level)),
                                     bg='#f8f9fa', fg='#495057',
                                     relief='solid', bd=1, width=20)
        self.customer_entry.grid(row=1, column=1, padx=8, pady=(0, 8), sticky="w")
        
        # Zoom controls
        zoom_frame = tk.Frame(scanner_frame, bg='#ffffff')
        zoom_frame.grid(row=1, column=2, padx=8)
        
        tk.Button(zoom_frame, text="-", command=self.zoom_out,
                 font=("Segoe UI", int(8 * self.zoom_level)), bg='#6c757d', fg='white',
                 width=2, relief='flat', bd=0).pack(side="left")
        tk.Button(zoom_frame, text="+", command=self.zoom_in,
                 font=("Segoe UI", int(8 * self.zoom_level)), bg='#6c757d', fg='white',
                 width=2, relief='flat', bd=0).pack(side="left")
    
    def create_compact_actions(self):
        """Create compact actions panel"""
        actions_frame = tk.Frame(self.root, bg='#ffffff', width=180)
        actions_frame.grid(row=1, column=0, sticky="ns", padx=(8, 4), pady=(0, 8))
        actions_frame.grid_propagate(False)
        
        # Compact action buttons
        ttk.Button(actions_frame, text="Inventory", command=self.secure_inventory_access,
                  style="Primary.TButton").pack(fill="x", padx=6, pady=3)
        
        ttk.Button(actions_frame, text="Clear Cart", command=self.clear_cart,
                  style="Danger.TButton").pack(fill="x", padx=6, pady=3)
        
        ttk.Button(actions_frame, text="Receipt", command=self.print_receipt,
                  style="Primary.TButton").pack(fill="x", padx=6, pady=3)
        
        # Compact total display
        total_frame = tk.Frame(actions_frame, bg='#e8f5e8', relief='solid', bd=1)
        total_frame.pack(fill="x", padx=6, pady=(12, 6))
        
        tk.Label(total_frame, text="TOTAL",
                font=("Segoe UI", int(10 * self.zoom_level), "bold"), fg='#495057', bg='#e8f5e8').pack(pady=(8, 2))
        
        self.total_var = tk.StringVar(value="0.00 DA")
        tk.Label(total_frame, textvariable=self.total_var,
                font=("Segoe UI", int(18 * self.zoom_level), "bold"),
                fg='#28a745', bg='#e8f5e8').pack(pady=(0, 8))
        
        self.item_count_var = tk.StringVar(value="0 items")
        tk.Label(total_frame, textvariable=self.item_count_var,
                font=("Segoe UI", int(8 * self.zoom_level)), fg='#6c757d', bg='#e8f5e8').pack(pady=(0, 6))
    
    def create_compact_cart(self):
        """Create compact cart display"""
        cart_frame = tk.Frame(self.root, bg='#ffffff')
        cart_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        cart_frame.grid_columnconfigure(0, weight=1)
        cart_frame.grid_rowconfigure(0, weight=1)
        
        # Compact cart treeview
        self.cart_tree = ttk.Treeview(cart_frame,
                                     columns=("Name", "Price", "Qty", "Subtotal"),
                                     show="headings",
                                     style="Cart.Treeview")
        
        # Compact headers
        self.cart_tree.heading("Name", text="Product")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Subtotal", text="Subtotal")
        
        # Optimized columns
        self.cart_tree.column("Name", width=200, anchor="w")
        self.cart_tree.column("Price", width=80, anchor="center")
        self.cart_tree.column("Qty", width=50, anchor="center")
        self.cart_tree.column("Subtotal", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Compact controls
        controls_frame = tk.Frame(cart_frame, bg='#ffffff', height=35)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        controls_frame.grid_propagate(False)
        
        ttk.Button(controls_frame, text="Remove", command=self.remove_item,
                  style="Danger.TButton").pack(side="left", padx=6, pady=6)
        
        ttk.Button(controls_frame, text="Edit Qty", command=self.edit_quantity,
                  style="Primary.TButton").pack(side="left", padx=6, pady=6)
        
        self.cart_tree.bind("<Double-1>", lambda e: self.edit_quantity())
    
    def create_compact_checkout(self):
        """Create compact checkout section"""
        checkout_frame = tk.Frame(self.root, bg='#ffffff', height=50)
        checkout_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        checkout_frame.grid_propagate(False)
        
        ttk.Button(checkout_frame, text="Complete Sale", command=self.checkout,
                  style="Success.TButton").pack(expand=True, pady=8)
    
    def process_search(self, event=None):
        """Process barcode or product name search"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
        
        # Try barcode first
        product = self.db.get_product_by_barcode(search_term)
        
        # If not found, try product name search
        if not product:
            products = self.db.get_all_products()
            matches = [p for p in products if search_term.lower() in p[2].lower()]
            
            if len(matches) == 1:
                product = matches[0]
            elif len(matches) > 1:
                # Show selection dialog for multiple matches
                product = self.select_from_matches(matches)
        
        if product:
            self.add_to_cart(product)
            self.barcode_entry.delete(0, tk.END)
        else:
            if messagebox.askyesno("Product Not Found",
                                 f"No product found for '{search_term}'.\nAdd new product?"):
                self.add_new_product(search_term)
        
        self.barcode_entry.focus_set()
    
    def select_from_matches(self, matches):
        """Show dialog to select from multiple product matches"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Product")
        dialog.geometry("400x300")
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.root)
        dialog.grab_set()
        
        selected_product = None
        
        listbox = tk.Listbox(dialog, font=("Segoe UI", 9))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for product in matches:
            listbox.insert(tk.END, f"{product[2]} - {product[3]:.2f} DA")
        
        def on_select():
            nonlocal selected_product
            selection = listbox.curselection()
            if selection:
                selected_product = matches[selection[0]]
                dialog.destroy()
        
        tk.Button(dialog, text="Select", command=on_select,
                 bg='#007bff', fg='white', relief='flat').pack(pady=5)
        
        dialog.wait_window()
        return selected_product
    
    def show_search_suggestions(self, *args):
        """Show search suggestions (simplified)"""
        # Could implement autocomplete dropdown here
        pass
    
    def handle_zoom(self, event):
        """Handle zoom with Ctrl+scroll"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 1.4:
            self.zoom_level += 0.1
            self.refresh_zoom()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.8:
            self.zoom_level -= 0.1
            self.refresh_zoom()
    
    def refresh_zoom(self):
        """Refresh UI with new zoom level"""
        self.setup_styles()
        self.cart_tree.configure(style="Cart.Treeview")
    
    def add_to_cart(self, product):
        """Add product to shopping cart"""
        product_id = product[0]
        
        if product[4] <= 0:
            messagebox.showwarning("Out of Stock", f"'{product[2]}' is out of stock!")
            return
        
        if product[4] < 5:
            messagebox.showwarning("Low Stock Warning", 
                                 f"Warning: Only {product[4]} units left for '{product[2]}'")
        
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] >= product[4]:
                messagebox.showwarning("Insufficient Stock", 
                                     f"Only {product[4]} units available for '{product[2]}'")
                return
            self.cart[product_id]['quantity'] += 1
        else:
            self.cart[product_id] = {
                'product': product,
                'quantity': 1
            }
        
        self.update_cart_display()
        self.update_total()

    def update_cart_display(self):
        """Update cart display with current items"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total_items = 0
        for product_id, item in self.cart.items():
            product = item['product']
            quantity = item['quantity']
            price = product[3]
            subtotal = price * quantity
            total_items += quantity
            
            self.cart_tree.insert("", "end", values=(
                product[2],  # name
                f"{price:.2f} DA",
                quantity,
                f"{subtotal:.2f} DA"
            ), tags=(product_id,))
        
        # Update item count
        self.item_count_var.set(f"{total_items} items")

    def update_total(self):
        """Update total amount display"""
        total = sum(item['product'][3] * item['quantity'] for item in self.cart.values())
        self.total_var.set(f"{total:.2f} DA")

    def checkout(self):
        """Process checkout and complete sale"""
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        total = sum(item['product'][3] * item['quantity'] for item in self.cart.values())
        customer_name = self.customer_entry.get().strip() or "Guest"
        
        sale_items = []
        for product_id, item in self.cart.items():
            quantity = item['quantity']
            subtotal = item['product'][3] * quantity
            sale_items.append((product_id, quantity, subtotal))
        
        if messagebox.askyesno("Confirm Sale", f"Process sale for {total:.2f} DA?\nCustomer: {customer_name}"):
            try:
                sale_id = self.db.record_sale(sale_items, total, customer_name)
                self.last_sale_id = sale_id
                
                messagebox.showinfo("Success", f"Sale completed!\nSale ID: {sale_id}\nTotal: {total:.2f} DA")
                
                self.cart.clear()
                self.customer_entry.delete(0, tk.END)
                self.update_cart_display()
                self.update_total()
                
                if messagebox.askyesno("Print Receipt", "Would you like to save a receipt?"):
                    self.print_receipt()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process sale: {str(e)}")

    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart and messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart.clear()
            self.update_cart_display()
            self.update_total()

    def remove_item(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        item = self.cart_tree.item(selection[0])
        if item['tags']:
            product_id = int(item['tags'][0])
            if product_id in self.cart:
                del self.cart[product_id]
                self.update_cart_display()
                self.update_total()

    def edit_quantity(self):
        """Edit quantity of selected item"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        item = self.cart_tree.item(selection[0])
        if item['tags']:
            product_id = int(item['tags'][0])
            if product_id in self.cart:
                current_qty = self.cart[product_id]['quantity']
                max_stock = self.cart[product_id]['product'][4]
                
                new_qty = simpledialog.askinteger(
                    "Edit Quantity", 
                    f"Enter new quantity (Max: {max_stock}):",
                    initialvalue=current_qty,
                    minvalue=1,
                    maxvalue=max_stock
                )
                
                if new_qty:
                    self.cart[product_id]['quantity'] = new_qty
                    self.update_cart_display()
                    self.update_total()

    def secure_inventory_access(self):
        """Secure access to inventory management"""
        password = simpledialog.askstring("Admin Access", "Enter admin password:", show='*')
        if password == self.admin_password:
            self.inventory_manager.open_inventory_window()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")

    def add_new_product(self, search_term):
        """Add new product via dialog"""
        from inventory_manager import ProductDialog
        dialog = ProductDialog(self.root, "Add New Product")
        if dialog.result:
            barcode, name, price, stock = dialog.result
            if self.db.add_product(barcode, name, price, stock):
                messagebox.showinfo("Success", "Product added successfully!")
                product = self.db.get_product_by_barcode(barcode)
                if product:
                    self.add_to_cart(product)

    def print_receipt(self):
        """Generate and save receipt as text file"""
        if not self.last_sale_id:
            messagebox.showwarning("Warning", "No recent sale to print!")
            return
        
        receipt_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Receipt"
        )
        
        if receipt_path:
            self.generate_receipt_file(receipt_path)

    def generate_receipt_file(self, filepath):
        """Generate receipt file content"""
        try:
            sale_data = self.db.get_sale_details(self.last_sale_id)
            customer_name = self.customer_entry.get().strip() or "Guest"
            
            with open(filepath, 'w') as f:
                f.write("=" * 40 + "\n")
                f.write("         POS SYSTEM RECEIPT\n")
                f.write("=" * 40 + "\n")
                f.write(f"Sale ID: {self.last_sale_id}\n")
                f.write(f"Customer: {customer_name}\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 40 + "\n")
                
                total = 0
                for item in sale_data:
                    name, price, qty, subtotal = item
                    f.write(f"{name:<20} {price:>6.2f} DA x{qty:>2} {subtotal:>7.2f} DA\n")
                    total += subtotal
                
                f.write("-" * 40 + "\n")
                f.write(f"{'TOTAL':<32} {total:>7.2f} DA\n")
                f.write("=" * 40 + "\n")
                f.write("Thank you for your purchase!\n")
            
            messagebox.showinfo("Success", f"Receipt saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")

    def auto_backup(self):
        """Automatic backup on startup"""
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        backup_path = os.path.join(backup_dir, f"auto_backup_{timestamp}.db")
        
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(self.db.db_path, backup_path)
            except Exception:
                pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Initialize with sample products if database is empty
    db = POSDatabase()
    products = db.get_all_products()
    
    if not products:
        sample_products = [
            ("1234567890123", "Sample Cola", 1.99, 50),
            ("2345678901234", "Sample Chips", 2.49, 30),
            ("3456789012345", "Sample Candy", 0.99, 100),
        ]
        
        for barcode, name, price, stock in sample_products:
            db.add_product(barcode, name, price, stock)
    
    pos = POSSystem()
    pos.run()
