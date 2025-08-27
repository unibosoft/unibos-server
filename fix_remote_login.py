#!/usr/bin/env python3
"""
Fix remote login by testing authentication directly
"""

import requests

# Test authentication
def test_login():
    url = "https://recaria.org/login/"
    
    # Get CSRF token
    session = requests.Session()
    response = session.get(url, verify=True)
    
    if 'csrfmiddlewaretoken' in response.text:
        # Extract CSRF token
        import re
        csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        
        if csrf_token:
            csrf = csrf_token.group(1)
            print(f"CSRF Token: {csrf[:30]}...")
            
            # Login data
            login_data = {
                'csrfmiddlewaretoken': csrf,
                'username': 'berkhatirli',
                'password': 'Admin123!',
                'next': '/'
            }
            
            # Headers
            headers = {
                'Referer': url,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Attempt login
            print("\nAttempting login...")
            login_response = session.post(url, data=login_data, headers=headers, allow_redirects=False)
            
            print(f"Status Code: {login_response.status_code}")
            
            if login_response.status_code == 302:
                print(f"Redirect Location: {login_response.headers.get('Location')}")
                
                # Check if sessionid cookie was set
                if 'sessionid' in session.cookies:
                    print("✅ Login successful! Session cookie set.")
                else:
                    print("⚠️ Redirect but no session cookie.")
                    
            elif login_response.status_code == 403:
                print("❌ 403 Forbidden - CSRF verification failed")
                print("\nResponse Headers:")
                for key, value in login_response.headers.items():
                    if key.lower() in ['x-csrf-failure-reason', 'x-error', 'server']:
                        print(f"  {key}: {value}")
            else:
                print(f"❌ Unexpected status code: {login_response.status_code}")
                
            # Check cookies
            print("\nCookies:")
            for cookie in session.cookies:
                print(f"  {cookie.name}: {cookie.value[:30]}...")
        else:
            print("❌ CSRF token not found in response")
    else:
        print("❌ Login page does not contain CSRF token")
        print(f"Page content preview: {response.text[:500]}")

if __name__ == "__main__":
    test_login()