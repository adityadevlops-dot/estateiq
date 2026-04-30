#!/usr/bin/env python3
"""
EstateIQ Integration Test Script
Verify that backend API and frontend are properly connected.
"""

import subprocess
import time
import sys
import json
from urllib.request import urlopen, Request
from urllib.error import URLError

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def print_status(status, message):
    """Print colored status message"""
    colors = {
        '✓': '\033[92m',      # Green
        '✗': '\033[91m',      # Red
        '⚠': '\033[93m',      # Yellow
        '🔄': '\033[94m',     # Blue
        'reset': '\033[0m'    # Reset
    }
    
    icon_color = colors.get(status[0], '')
    print(f"{icon_color}{status}{colors['reset']} {message}")

def test_api_health():
    """Test if backend API is running"""
    print_status('🔄', 'Testing API health...')
    
    try:
        req = Request('http://localhost:5000/health')
        req.add_header('Accept', 'application/json')
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print_status('✓', f"API is running: {data.get('status', 'unknown')}")
            return True
    except URLError as e:
        print_status('✗', f"API not accessible: {e.reason}")
        return False
    except Exception as e:
        print_status('✗', f"API check failed: {str(e)}")
        return False

def test_models_loaded():
    """Test if ML models are loaded"""
    print_status('🔄', 'Checking if ML models are loaded...')
    
    try:
        req = Request('http://localhost:5000/api/metrics')
        req.add_header('Accept', 'application/json')
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get('success') and data.get('data'):
                r2_score = data['data'].get('model_r2_score', 0)
                print_status('✓', f"Models loaded. Best R² score: {r2_score:.4f} ({r2_score*100:.2f}%)")
                return True
            else:
                print_status('✗', "No model metrics found")
                return False
    except URLError as e:
        print_status('✗', f"Could not fetch metrics: {e.reason}")
        return False
    except Exception as e:
        print_status('✗', f"Model check failed: {str(e)}")
        return False

def test_prediction_endpoint():
    """Test if prediction endpoint works"""
    print_status('🔄', 'Testing prediction endpoint...')
    
    try:
        test_data = {
            'area_sqft': 2000,
            'location': 'Mumbai',
            'bedrooms': 3,
            'bathrooms': 2,
            'age_years': 5,
            'floor': 10,
            'furnishing': 'Semi-Furnished',
            'parking': 1
        }
        
        json_data = json.dumps(test_data).encode('utf-8')
        req = Request(
            'http://localhost:5000/api/predict',
            data=json_data,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            method='POST'
        )
        
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                price = data['data'].get('predicted_price')
                confidence = data['data'].get('confidence_range', {}).get('confidence', 0)
                print_status('✓', f"Prediction successful: ₹{price:,} (Confidence: {confidence*100:.1f}%)")
                return True
            else:
                error = data.get('error', 'Unknown error')
                print_status('✗', f"Prediction failed: {error}")
                return False
                
    except URLError as e:
        print_status('✗', f"Prediction request failed: {e.reason}")
        return False
    except Exception as e:
        print_status('✗', f"Prediction test failed: {str(e)}")
        return False

def test_cors_headers():
    """Test if CORS headers are present"""
    print_status('🔄', 'Checking CORS headers...')
    
    try:
        req = Request('http://localhost:5000/api/metrics')
        with urlopen(req, timeout=5) as response:
            headers = response.headers
            
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            found = sum(1 for h in cors_headers if h in headers)
            
            if found > 0:
                print_status('✓', f"CORS enabled ({found}/3 headers found)")
                return True
            else:
                print_status('⚠', "CORS headers not found (frontend may have issues)")
                return False
                
    except Exception as e:
        print_status('✗', f"CORS check failed: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  🏠 EstateIQ Integration Test Suite")
    print("="*60 + "\n")
    
    print("Prerequisites:")
    print("  1. Backend API running on http://localhost:5000")
    print("  2. ML models trained (run: python train.py)")
    print("\n" + "-"*60 + "\n")
    
    results = {
        'health': test_api_health(),
        'models': test_models_loaded(),
        'prediction': test_prediction_endpoint(),
        'cors': test_cors_headers()
    }
    
    print("\n" + "-"*60)
    print("\n📊 Test Results:")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = '✓' if result else '✗'
        print_status(status, f"{test_name.capitalize()}")
    
    print(f"\nPassed: {passed}/{total}\n")
    
    if passed == total:
        print_status('✓', "All tests passed! 🎉")
        print("\nNext steps:")
        print("  1. Frontend: http://localhost:8000")
        print("  2. Navigate to Predict page")
        print("  3. Fill in property details")
        print("  4. Submit to get live prediction\n")
        return 0
    else:
        print_status('✗', "Some tests failed")
        print("\nTroubleshooting:")
        
        if not results['health']:
            print("  • Start backend: cd backend && python run_api.py")
        
        if not results['models']:
            print("  • Train models: cd backend && python train.py")
        
        if not results['prediction']:
            print("  • Check backend logs for prediction errors")
        
        if not results['cors']:
            print("  • Verify CORS is enabled in backend/api/app.py")
        
        print()
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted")
        sys.exit(1)
