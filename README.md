# Offline POS System

A complete offline Point of Sale system designed for barcode scanning via phone, inventory management, and sales recording.

## Features

- **Barcode Scanning**: Use your phone as a barcode scanner (HID input)
- **Offline Database**: SQLite-based storage, no internet required
- **Inventory Management**: Add, edit, delete products and manage stock
- **Sales Recording**: Complete transaction logging with timestamps
- **Real-time Cart**: Live cart updates with quantity management
- **Stock Warnings**: Low stock alerts (below 5 units)
- **Export Functionality**: Export inventory to CSV

## Setup Instructions

1. **Install Python 3.7+** (tkinter included)

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Phone Setup**:
   - Install a barcode scanner app that outputs as keyboard input
   - Connect phone via USB/WiFi to computer
   - Configure as HID device
   - Scanned barcodes will appear in the barcode input field

## Usage

### Main POS Interface
- **Barcode Field**: Auto-focused for phone scanner input
- **Add Product**: Manual barcode entry or scan
- **Shopping Cart**: Real-time display of scanned items
- **Checkout**: Process sale and update inventory

### Inventory Management
- Access via "Inventory Management" button
- Add new products with barcode, name, price, stock
- Edit existing products
- Delete products
- Export inventory to CSV
- Stock level monitoring

### Checkout Process
1. Scan products (adds to cart automatically)
2. Adjust quantities if needed
3. Click "Checkout" to finalize sale
4. Inventory automatically updated

## Database Structure

- **products**: barcode, name, price, stock
- **sales**: timestamp, total_amount
- **sale_items**: sale_id, product_id, quantity, subtotal

## Files

- `main.py`: Main POS interface
- `database.py`: SQLite database operations
- `inventory_manager.py`: Inventory management interface
- `pos_system.db`: SQLite database (created automatically)

## Phone Scanner Setup

1. **Android**: Use "Barcode Scanner +" or similar apps with HID keyboard mode
2. **iPhone**: Use "Scan" app or similar with keyboard output
3. **Connection**: USB preferred for reliability, WiFi as alternative
4. **Configuration**: Set scanner to send data as keyboard input with Enter/Return after each scan

## Security Features

- Admin access to inventory management
- Local database backup capability
- No network dependencies

## Deployment

To create standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The system will run completely offline once deployed.
