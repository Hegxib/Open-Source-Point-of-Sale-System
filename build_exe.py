import os
import subprocess
import shutil

def build_pos_exe():
    """Build POS system into executable"""
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('main.spec'):
        os.remove('main.spec')
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single exe file
        '--windowed',                   # No console window
        '--name=POS_System',           # Custom exe name
        '--icon=icon.ico',             # Add icon if you have one
        '--add-data=pos_database.db;.', # Include database
        '--hidden-import=tkinter',      # Ensure tkinter is included
        '--hidden-import=sqlite3',      # Ensure sqlite3 is included
        'main.py'
    ]
    
    try:
        print("Building POS System executable...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"📁 Executable location: {os.path.abspath('dist/POS_System.exe')}")
            
            # Create a simple installer folder
            installer_dir = "POS_Installer"
            if os.path.exists(installer_dir):
                shutil.rmtree(installer_dir)
            os.makedirs(installer_dir)
            
            # Copy exe and create sample database
            shutil.copy('dist/POS_System.exe', installer_dir)
            
            # Create README
            with open(f'{installer_dir}/README.txt', 'w') as f:
                f.write("""POS System Installation
=====================

1. Run POS_System.exe to start the application
2. Default admin password: admin123
3. The system will create a database automatically on first run

Features:
- Barcode scanning and product search
- Inventory management
- Sales tracking
- Receipt generation
- Automatic backups

Support: Check the source code for customization options.
""")
            
            print(f"📦 Installer package created: {os.path.abspath(installer_dir)}")
            
        else:
            print("❌ Build failed!")
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"❌ Build error: {e}")

if __name__ == "__main__":
    build_pos_exe()
