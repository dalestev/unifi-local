import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Initial setup
base_url = "https://192.168.0.191"
login_endpoint = "/api/auth/login"
snapshot_endpoint = "/proxy/protect/api/cameras/{camera_id}/snapshot"
camera_id = "663bdea100587703e400040c"  # Replace with actual camera ID
username = "username" # Replace with username
password = "password" # Replace with password


def make_post_request(url, headers, body):
    try:
        response = requests.post(url, headers=headers, json=body, verify=False)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"POST request failed: {e}")
        return None

def make_get_request(url, headers, cookies):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"GET request failed: {e}")
        return None

# Step 1: Prompt for MFA token
mfa_token = input("Enter MFA token: ")

# Step 2: Make a POST request to the login endpoint with user credentials and MFA token
login_response = make_post_request(
    url=base_url + login_endpoint,
    headers={
        "Content-Type": "application/json"
    },
    body={
        "username": username,
        "password": password,
        "token": mfa_token,
        "rememberMe": False
    }
)

# Step 3: Check if login was successful
if login_response and login_response.status_code == 200:
    print("Login successful.")
    print("Login response cookies:", login_response.cookies)
    
    # Step 4: Extract auth token from response cookies
    auth_token = login_response.cookies.get('TOKEN')
    
    # Step 5: Extract CSRF token from cookies
    csrf_token = login_response.cookies.get('CSRF-TOKEN')
    
    # Step 6: Make an authenticated GET request to fetch the camera snapshot using the auth token and CSRF token
    if auth_token:
        cookies = login_response.cookies.get_dict()
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        if csrf_token:
            headers["X-Csrf-Token"] = csrf_token
        
        snapshot_url = base_url + snapshot_endpoint.format(camera_id=camera_id) + "?ts=" + str(int(time.time() * 1000))
        
        snapshot_response = make_get_request(
            url=snapshot_url,
            headers=headers,
            cookies=cookies
        )
        
        # Step 7: Check if fetching the snapshot was successful
        if snapshot_response and snapshot_response.status_code == 200:
            with open("camera_snapshot.jpg", "wb") as image_file:
                image_file.write(snapshot_response.content)
            print("Snapshot fetched and saved as 'camera_snapshot.jpg'.")
        else:
            print("Failed to fetch snapshot:", snapshot_response.status_code if snapshot_response else "No response")
    else:
        print("Failed to retrieve auth token")
else:
    print("Login failed with status code:", login_response.status_code if login_response else "No response")
