#!/usr/bin/env python3
"""
Test script to verify percentile validation fix
"""

import json
from app import validate_percentile, generate_all_templates
import os

def test_percentile_validation():
    """Test percentile validation with various inputs"""
    print("🧪 Testing Percentile Validation")
    print("=" * 40)
    
    test_cases = [
        (0.0, True, "Zero"),
        (5.5, True, "Positive valid"),
        (-5.5, True, "Negative valid"),
        (-99.99, True, "Minimum valid"),
        (9.99, True, "Maximum valid"),
        (10.0, False, "Above maximum"),
        (-100.0, False, "Below minimum"),
        ("", False, "Empty string"),
        (None, False, "None"),
        ("abc", False, "Invalid string"),
        (0, True, "Integer zero"),
        (5, True, "Integer positive"),
        (-5, True, "Integer negative")
    ]
    
    passed = 0
    for value, expected, description in test_cases:
        result, message = validate_percentile(value)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: {value} -> {result} ({message})")
        if result == expected:
            passed += 1
    
    print(f"\n📊 {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_sample_data():
    """Test with sample data that might cause the work 9 error"""
    print("\n🧪 Testing Sample Data Generation")
    print("=" * 40)
    
    # Create sample data with 10 works
    sample_data = {
        'nit_info': {'nit_number': '03/2025-26'},
        'works': []
    }
    
    # Create 10 works with bidders
    for i in range(10):
        work = {
            'name': f'WORK {i + 1}',
            'bidders': []
        }
        
        # Add 3 bidders per work with valid percentiles
        for j in range(3):
            bidder = {
                'name': f'Bidder {j + 1}',
                'percentile': 0.0  # Valid percentile
            }
            work['bidders'].append(bidder)
        
        sample_data['works'].append(work)
    
    try:
        # Test template generation
        output_dir = "test_output_percentile_fix"
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = generate_all_templates(sample_data, output_dir)
        
        print(f"✅ Successfully generated {len(generated_files)} templates")
        for file_path in generated_files:
            file_size = os.path.getsize(file_path)
            print(f"   📄 {os.path.basename(file_path)}: {file_size} bytes")
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
        print("🧹 Test files cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 40)
    
    # Test with empty bidders
    try:
        sample_data = {
            'nit_info': {'nit_number': 'TEST'},
            'works': [{
                'name': 'TEST WORK',
                'bidders': []  # Empty bidders
            }]
        }
        
        output_dir = "test_output_edge_cases"
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = generate_all_templates(sample_data, output_dir)
        print("✅ Handled empty bidders correctly")
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
        
    except Exception as e:
        print(f"❌ Error with empty bidders: {str(e)}")
        return False
    
    # Test with invalid percentiles
    invalid_cases = [
        {'percentile': 10.0, 'expected': False},
        {'percentile': -100.0, 'expected': False},
        {'percentile': None, 'expected': False},
        {'percentile': '', 'expected': False}
    ]
    
    for case in invalid_cases:
        result, message = validate_percentile(case['percentile'])
        if result == case['expected']:
            print(f"✅ Invalid case handled: {case['percentile']}")
        else:
            print(f"❌ Invalid case failed: {case['percentile']}")
            return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Percentile Validation Fix")
    print("=" * 50)
    
    # Test 1: Percentile validation
    test1_passed = test_percentile_validation()
    
    # Test 2: Sample data generation
    test2_passed = test_sample_data()
    
    # Test 3: Edge cases
    test3_passed = test_edge_cases()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Percentile Validation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Sample Data Generation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Edge Cases: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! The percentile validation fix is working correctly.")
        print("✅ The 'invalid percentage for work 9' error should now be resolved.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
