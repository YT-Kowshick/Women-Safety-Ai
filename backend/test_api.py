"""
Test script for Women Safety AI API
Run this after starting the server to verify all endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_test(name, status):
    """Print test result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")

def test_health():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200 and response.json() == {"status": "ok"}
        print_test("Health Check", success)
        return success
    except Exception as e:
        print_test(f"Health Check (Error: {e})", False)
        return False

def test_predict_safety():
    """Test safety prediction endpoint"""
    try:
        payload = {
            "state": "Tamil Nadu",
            "year": 2021
        }
        response = requests.post(
            f"{BASE_URL}/predict/safety",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(k in data for k in ["state", "year", "safety_score", "risk_level"])
            valid_risk = data.get("risk_level") in ["Low", "Medium", "High"]
            success = has_required_fields and valid_risk
            print_test(f"Predict Safety (Score: {data.get('safety_score', 'N/A')}, Risk: {data.get('risk_level', 'N/A')})", success)
            return success
        else:
            print_test(f"Predict Safety (Status: {response.status_code})", False)
            return False
    except Exception as e:
        print_test(f"Predict Safety (Error: {e})", False)
        return False

def test_simulate():
    """Test simulation endpoint"""
    try:
        payload = {
            "year": 2021,
            "rape": 100,
            "kidnapping": 50,
            "dowry_deaths": 20,
            "assault_on_women": 150,
            "assault_on_minors": 30,
            "domestic_violence": 80,
            "trafficking": 10
        }
        response = requests.post(
            f"{BASE_URL}/predict/simulate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(k in data for k in ["safety_score", "risk_level"])
            valid_risk = data.get("risk_level") in ["Low", "Medium", "High"]
            success = has_required_fields and valid_risk
            print_test(f"Simulate (Score: {data.get('safety_score', 'N/A')}, Risk: {data.get('risk_level', 'N/A')})", success)
            return success
        else:
            print_test(f"Simulate (Status: {response.status_code})", False)
            return False
    except Exception as e:
        print_test(f"Simulate (Error: {e})", False)
        return False

def test_trends():
    """Test trends endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/trends",
            params={"state": "Andhra Pradesh", "crime": "Rape"}
        )
        
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(k in data for k in ["state", "crime", "data"])
            has_data = len(data.get("data", [])) > 0
            success = has_required_fields and has_data
            print_test(f"Trends (Data points: {len(data.get('data', []))})", success)
            return success
        else:
            print_test(f"Trends (Status: {response.status_code})", False)
            return False
    except Exception as e:
        print_test(f"Trends (Error: {e})", False)
        return False

def test_leaderboard():
    """Test leaderboard endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/leaderboard")
        
        if response.status_code == 200:
            data = response.json()
            is_list = isinstance(data, list)
            has_entries = len(data) > 0
            valid_format = all("state" in entry and "score" in entry for entry in data[:3])
            success = is_list and has_entries and valid_format
            print_test(f"Leaderboard (States: {len(data)})", success)
            return success
        else:
            print_test(f"Leaderboard (Status: {response.status_code})", False)
            return False
    except Exception as e:
        print_test(f"Leaderboard (Error: {e})", False)
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    try:
        # Test invalid state
        payload = {"state": "InvalidState", "year": 2021}
        response = requests.post(f"{BASE_URL}/predict/safety", json=payload)
        test1 = response.status_code == 404
        
        # Test invalid year range
        payload = {"state": "Tamil Nadu", "year": 1990}
        response = requests.post(f"{BASE_URL}/predict/safety", json=payload)
        test2 = response.status_code == 422
        
        # Test invalid crime type
        response = requests.get(f"{BASE_URL}/trends", params={"state": "Delhi", "crime": "InvalidCrime"})
        test3 = response.status_code == 400
        
        success = test1 and test2 and test3
        print_test("Error Handling", success)
        return success
    except Exception as e:
        print_test(f"Error Handling (Error: {e})", False)
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*50)
    print("Women Safety AI - API Tests")
    print("="*50 + "\n")
    
    tests = [
        test_health,
        test_predict_safety,
        test_simulate,
        test_trends,
        test_leaderboard,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    print("="*50 + "\n")

if __name__ == "__main__":
    print("\nMake sure the server is running: uvicorn app:app --reload\n")
    
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on http://localhost:8000?")
        print("   Start it with: uvicorn app:app --reload")
