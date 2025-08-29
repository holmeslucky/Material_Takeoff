#!/usr/bin/env python3
"""
Test script to verify project creation API works
"""
import requests
import json

def test_create_project():
    # Test data matching the CreateProject form
    project_data = {
        "name": "Test Takeoff Project",
        "client": "Test Customer LLC",
        "location": "Phoenix, AZ",
        "description": "Test project for API integration",
        "status": "active",
        "quote_number": "25-TEST01",
        "estimator": "Blake Holmes",
        "date": "2025-08-22"
    }
    
    try:
        print("Testing project creation API...")
        
        # Test POST /api/v1/projects
        response = requests.post(
            "http://localhost:8000/api/v1/projects/",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            project = response.json()
            print("Project created successfully!")
            print(f"   - ID: {project.get('id')}")
            print(f"   - Name: {project.get('name')}")
            print(f"   - Client: {project.get('client_name')}")
            return project
        else:
            print(f"Failed to create project: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error testing project creation: {e}")
        return None

def test_get_projects():
    try:
        print("\nTesting get projects API...")
        
        # Test GET /api/v1/projects
        response = requests.get("http://localhost:8000/api/v1/projects/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects)} projects")
            for project in projects:
                print(f"   - {project.get('name')} ({project.get('client_name')})")
        else:
            print(f"Failed to get projects: {response.text}")
            
    except Exception as e:
        print(f"Error testing get projects: {e}")

if __name__ == "__main__":
    print("Testing Project Creation API Integration")
    print("=" * 50)
    
    project = test_create_project()
    test_get_projects()
    
    print("\n" + "=" * 50)
    print("API Integration Test Complete!")