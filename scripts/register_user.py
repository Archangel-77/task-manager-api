import httpx

url = "http://127.0.0.1:8000/auth/register"
data = {
    "username": "testuser",
    "password": "password123"
}

response = httpx.post(url, json=data)
print(response.json())