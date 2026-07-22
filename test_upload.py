import requests
import io

url = "http://localhost:8000/api/v1/resume/upload"
files = {'file': ('test.pdf', b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n', 'application/pdf')}

try:
    response = requests.post(url, files=files)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.text)
except Exception as e:
    print("Failed to connect:", e)
