#!/usr/bin/env python3
"""
Simple test script to check plate calculation error handling
"""

import requests
import json

def test_plate_error():
    """Test plate calculation without width"""
    
    url = "http://localhost:8000/api/v1/takeoff/calculate"
    
    test_data = {
        "qty": 5,
        "shape_key": "PL1/2X12",
        "length_ft": 10.0,
        "width_ft": 0.0,
        "unit_price_per_cwt": 85.00,
        "calculate_labor": False,
        "labor_mode": "auto"
    }
    
    print("Testing plate calculation without width...")
    print(f"Request: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("SUCCESS: Got 400 Bad Request (expected)")
            detail = response.json().get('detail', '')
            if 'width_ft' in detail:
                print("SUCCESS: Error message mentions width requirement")
            return True
        elif response.status_code == 500:
            print("FAIL: Still getting 500 Internal Server Error")
            return False
        else:
            print(f"UNEXPECTED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_plate_success():
    """Test plate calculation with proper width"""
    
    url = "http://localhost:8000/api/v1/takeoff/calculate"
    
    test_data = {
        "qty": 5,
        "shape_key": "PL1/2X12", 
        "length_ft": 10.0,
        "width_ft": 4.0,
        "unit_price_per_cwt": 85.00,
        "calculate_labor": False,
        "labor_mode": "auto"
    }
    
    print("\nTesting plate calculation with width...")
    print(f"Request: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Plate calculation worked")
            print(f"Total weight: {data.get('total_weight_lbs', 0)} lbs")
            print(f"Total price: ${data.get('total_price', 0)}")
            return True
        else:
            print(f"FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=== Plate Logic Error Handling Test ===")
    
    error_test = test_plate_error()
    success_test = test_plate_success()
    
    print(f"\nResults:")
    print(f"Error handling test: {'PASS' if error_test else 'FAIL'}")  
    print(f"Success test: {'PASS' if success_test else 'FAIL'}")
    
    if error_test and success_test:
        print("\nAll tests PASSED - Plate logic is working correctly!")
    else:
        print("\nSome tests FAILED - Plate logic needs more work")