import sqlite3
import datetime
from typing import List, Tuple, Optional

class POSDatabase:
    def __init__(self, db_path: str = "pos_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Updated sales table with customer name
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_amount REAL NOT NULL,
                customer_name TEXT DEFAULT 'Guest'
            )
        ''')
        
        # Sale items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, barcode: str, name: str, price: float, stock: int) -> bool:
        """Add new product to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (barcode, name, price, stock) VALUES (?, ?, ?, ?)",
                (barcode, name, price, stock)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Tuple]:
        """Get product by barcode"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        product = cursor.fetchone()
        conn.close()
        return product
    
    def update_stock(self, product_id: int, new_stock: int):
        """Update product stock"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        conn.commit()
        conn.close()
    
    def record_sale(self, cart_items: List[Tuple], total: float, customer_name: str = "Guest") -> int:
        """Record sale with customer name and return sale ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute("INSERT INTO sales (timestamp, total_amount, customer_name) VALUES (?, ?, ?)", 
                      (timestamp, total, customer_name))
        sale_id = cursor.lastrowid
        
        # Insert sale items and update stock
        for product_id, quantity, subtotal in cart_items:
            cursor.execute(
                "INSERT INTO sale_items (sale_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                (sale_id, product_id, quantity, subtotal)
            )
            
            # Update stock
            cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            current_stock = cursor.fetchone()[0]
            new_stock = max(0, current_stock - quantity)
            cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        
        conn.commit()
        conn.close()
        return sale_id
    
    def get_sale_details(self, sale_id: int) -> List[Tuple]:
        """Get detailed sale information for receipt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.price, si.quantity, si.subtotal
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        """, (sale_id,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    def get_all_products(self) -> List[Tuple]:
        """Get all products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        products = cursor.fetchall()
        conn.close()
        return products
    
    def delete_product(self, product_id: int):
        """Delete product by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
    
    def update_product(self, product_id: int, name: str, price: float, stock: int):
        """Update product details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?",
            (name, price, stock, product_id)
        )
        conn.commit()
        conn.close()
