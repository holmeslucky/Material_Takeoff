#!/usr/bin/env python3
"""
Test script to check plate calculation error handling
"""

import requests
import json

def test_plate_without_width():
    """Test plate calculation without width to verify error handling"""
    
    url = "http://localhost:8000/api/v1/takeoff/calculate"
    
    # Test data for a plate without width (should trigger error)
    test_data = {
        "qty": 5,
        "shape_key": "PL1/2X12",
        "length_ft": 10.0,
        "width_ft": 0.0,  # This should trigger the error
        "unit_price_per_cwt": 85.00,
        "calculate_labor": False,
        "labor_mode": "auto"
    }
    
    print("Testing plate calculation without width...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("\n✅ SUCCESS: Got expected 400 Bad Request error")
            error_msg = response.json().get('detail', '')
            if 'width_ft > 0' in error_msg:
                print("✅ SUCCESS: Error message contains expected text about width requirement")
            else:
                print("❌ WARNING: Error message doesn't mention width requirement")
        elif response.status_code == 500:
            print("\n❌ FAIL: Still getting 500 Internal Server Error (error handling not working)")
        else:
            print(f"\n❓ UNEXPECTED: Got status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: Failed to make request: {e}")

def test_plate_with_width():
    """Test plate calculation with width to verify normal operation"""
    
    url = "http://localhost:8000/api/v1/takeoff/calculate"
    
    # Test data for a plate with proper width (should work)
    test_data = {
        "qty": 5,
        "shape_key": "PL1/2X12",
        "length_ft": 10.0,
        "width_ft": 4.0,  # Proper width provided
        "unit_price_per_cwt": 85.00,
        "calculate_labor": False,
        "labor_mode": "auto"
    }
    
    print("\nTesting plate calculation with width...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Plate calculation worked with proper width")
        else:
            print(f"\n❌ FAIL: Expected 200 OK, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: Failed to make request: {e}")

if __name__ == "__main__":
    print("=== Plate Logic Error Handling Test ===")
    print()
    
    test_plate_without_width()
    test_plate_with_width()
    
    print("\n=== Test Complete ===")