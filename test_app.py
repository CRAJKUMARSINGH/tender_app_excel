#!/usr/bin/env python3
"""
Test script for the Tender Processing Application
This script tests the core functionality without running the web server
"""

import os
import sys
import pandas as pd
from datetime import datetime
import pytest

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import parse_input_file, create_excel_template, validate_percentile, generate_all_templates

@pytest.fixture
def data():
    """Provide parsed data for template generation tests if test file exists."""
    test_file = "input_DATA/NIT_10 works_1753162653002.xlsx"
    if os.path.exists(test_file):
        try:
            return parse_input_file(test_file)
        except Exception:
            return None
    return None

def test_parse_input_file():
    """Test the input file parsing functionality"""
    print("🧪 Testing input file parsing...")
    
    # Test with the existing input file
    test_file = "input_DATA/NIT_10 works_1753162653002.xlsx"
    
    if os.path.exists(test_file):
        try:
            data = parse_input_file(test_file)
            print("✅ File parsing successful!")
            print(f"   - NIT Number: {data['nit_info'].get('nit_number', 'N/A')}")
            print(f"   - Number of works: {len(data['works'])}")
            print(f"   - Works: {[work['name'] for work in data['works']]}")
            return data
        except Exception as e:
            print(f"❌ File parsing failed: {str(e)}")
            return None
    else:
        print(f"❌ Test file not found: {test_file}")
        return None

def test_validation():
    """Test the percentile validation functionality"""
    print("\n🧪 Testing percentile validation...")
    
    test_cases = [
        (-99.99, True),   # Valid minimum
        (0.00, True),     # Valid zero
        (9.99, True),     # Valid maximum
        (-100.00, False), # Invalid below minimum
        (10.00, False),   # Invalid above maximum
        ("abc", False),   # Invalid string
        (None, False),    # Invalid None
    ]
    
    all_passed = True
    for value, expected in test_cases:
        result = validate_percentile(value)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {value} -> {result} (expected {expected})")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("✅ All validation tests passed!")
    else:
        print("❌ Some validation tests failed!")
    
    return all_passed

def test_template_generation(data):
    """Test the template generation functionality"""
    print("\n🧪 Testing template generation...")
    
    if not data:
        print("❌ No data available for template generation")
        return False
    
    try:
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate templates
        generated_files = generate_all_templates(data, output_dir)
        
        print(f"✅ Template generation successful!")
        print(f"   - Generated {len(generated_files)} templates:")
        for file_path in generated_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            print(f"     • {file_name} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Template generation failed: {str(e)}")
        return False

def test_excel_creation():
    """Test individual Excel template creation"""
    print("\n🧪 Testing Excel template creation...")
    
    # Sample data
    sample_data = {
        'nit_info': {
            'nit_number': 'TEST-2024-001',
            'opening_date': '2024-01-15',
            'calling_date': '2024-01-01',
            'receipt_date': '2024-01-10'
        },
        'works': [
            {
                'item_no': 1,
                'name': 'Test Work 1',
                'time_completion': '3 months',
                'earnest_money': '5000'
            },
            {
                'item_no': 2,
                'name': 'Test Work 2',
                'time_completion': '6 months',
                'earnest_money': '7500'
            }
        ]
    }
    
    try:
        # Test each template type
        templates = ['comparison', 'scrutiny', 'evaluation', 'award']
        
        for template in templates:
            output_path = f"test_output/test_{template}.xlsx"
            success = create_excel_template(sample_data, template, output_path)
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ {template.title()} template created ({file_size} bytes)")
            else:
                print(f"   ❌ {template.title()} template creation failed")
                return False
        
        print("✅ All Excel templates created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Excel creation test failed: {str(e)}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_dir = "test_output"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
        print("✅ Test files cleaned up")
    else:
        print("ℹ️  No test files to clean up")

def main():
    """Main test function"""
    print("🚀 Starting Tender Processing Application Tests")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Input File Parsing", test_parse_input_file),
        ("Data Validation", test_validation),
        ("Excel Template Creation", test_excel_creation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_name == "Input File Parsing":
            result = test_func()
            results[test_name] = result is not None
            if result:
                # Use the parsed data for template generation test
                results["Template Generation"] = test_template_generation(result)
        else:
            results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
