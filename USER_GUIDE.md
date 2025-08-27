# 📖 Simple User Guide - Tender Processing System

## 🚀 **Quick Start (For Non-Technical Users)**

### **Step 1: First Time Setup**
1. **Double-click** `INSTALL_AND_SETUP.bat`
2. Wait for the installation to complete
3. You'll see "SETUP COMPLETE!" when done

### **Step 2: Start the Application**
1. **Double-click** `START_APP.bat`
2. Your browser will open automatically
3. If browser doesn't open, go to: `http://localhost:5000`

### **Step 3: Use the Application**
1. **Upload your Excel file** (drag & drop or click to browse)
2. **Review the data** that appears
3. **Enter bidder information** for each work
4. **Click "Generate Templates"**
5. **Download your results**

## 📋 **What You Need**

### **Input Files**
- Excel files (.xlsx or .xls format)
- Maximum file size: 10MB
- Should contain NIT information and works data

### **System Requirements**
- Windows 10 or higher
- Internet connection (for first-time setup)
- Web browser (Chrome, Firefox, Edge, etc.)

## 🎯 **What the Application Does**

### **Generates 4 Professional Templates:**
1. **Comparison Sheet** - A4 Landscape format
2. **Scrutiny Sheet** - A4 Portrait format
3. **Evaluation Sheet** - A4 Portrait format
4. **Award Sheet** - A4 Portrait format

### **Features:**
- ✅ **Automatic data extraction** from Excel files
- ✅ **Professional formatting** with borders
- ✅ **Box image** superimposed on comparison sheets
- ✅ **Data validation** for percentile scores
- ✅ **Error handling** and user-friendly messages

## 📊 **Percentile Rules**

### **Valid Range:**
- **Minimum**: -99.99%
- **Maximum**: +99.99%
- **Inclusive**: 0.00% is valid

### **Examples:**
- ✅ -5.25% (valid)
- ✅ 0.00% (valid)
- ✅ 2.75% (valid)
- ❌ -100.00% (invalid)
- ❌ 10.00% (invalid)

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. "Python is not installed"**
- Download Python from https://python.org
- Run the installer
- Check "Add Python to PATH"
- Restart the batch file

**2. "File upload failed"**
- Check file format (.xlsx or .xls only)
- Ensure file size is under 10MB
- Make sure file is not corrupted

**3. "Application won't start"**
- Check if another application is using port 5000
- Try closing and reopening the batch file
- Restart your computer if needed

**4. "Browser doesn't open automatically"**
- Manually go to: `http://localhost:5000`
- Or try: `http://127.0.0.1:5000`

## 📁 **File Locations**

### **Input Files:**
- Place your Excel files in the `input_DATA` folder
- Or upload directly through the web interface

### **Output Files:**
- Generated templates are saved in the `outputs` folder
- Each run creates a timestamped folder
- Files are automatically downloaded to your Downloads folder

## 🆘 **Getting Help**

### **If Something Goes Wrong:**
1. Check the error message on screen
2. Try restarting the application
3. Check this user guide
4. Read the detailed README.md file

### **Contact Information:**
- For technical support, check the README.md file
- Application logs are saved for debugging

## 🎉 **Success Tips**

1. **Always backup** your original Excel files
2. **Test with small files** first
3. **Check the preview** before generating templates
4. **Save your work** regularly
5. **Keep the application updated**

---

**🎯 Remember: This application replaces your old VBA macro with a modern, reliable, and user-friendly solution!**
