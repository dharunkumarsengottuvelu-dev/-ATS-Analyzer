import requests

url = "http://127.0.0.1:8000/api/v1/resume/upload"

# Create a dummy PDF with more than 50 characters to avoid OCR fallback
dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n10 10 Td\n(This is a dummy PDF file with a lot of text so it does not trigger the OCR fallback! It needs to be more than 50 characters long to pass the threshold.) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000219 00000 n \n0000000307 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n402\n%%EOF"

files = {'file': ('test.pdf', dummy_pdf_content, 'application/pdf')}
response = requests.post(url, files=files)

print(response.status_code)
print(response.text)
