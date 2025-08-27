#!/usr/bin/env python3
"""
Startup script for the Tender Processing Application
This script launches the web application with proper configuration
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open the web browser to the application"""
    webbrowser.open('http://localhost:5000')

def main():
    """Main startup function"""
    print("🚀 Starting Tender Processing Application...")
    print("=" * 50)
    
    # Check if required directories exist
    required_dirs = ['uploads', 'outputs', 'templates']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Check if required files exist
    required_files = ['app.py', 'templates/index.html', 'requirements.txt']
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files and directories found")
    
    # Import and run the Flask app
    try:
        from app import app
        
        print("✅ Flask application loaded successfully")
        print("🌐 Starting web server...")
        print("📱 The application will open in your browser automatically")
        print("🔗 Manual access: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Open browser after a short delay
        Timer(2.0, open_browser).start()
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {str(e)}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
