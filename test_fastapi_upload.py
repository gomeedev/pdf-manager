import os
import requests
from uuid import uuid4
from supabase import create_client
from core.config import settings

def test_upload():
    service_client = create_client(settings.supabase_url, settings.supabase_service_key)
    
    email = f"testapi_{uuid4()}@example.com"
    password = "password123"
    
    # 1. Create User
    user_resp = service_client.auth.admin.create_user({"email": email, "password": password, "email_confirm": True})
    user_id = user_resp.user.id
    
    # 2. Login
    auth_resp = service_client.auth.sign_in_with_password({"email": email, "password": password})
    token = auth_resp.session.access_token
    
    # 3. Create a dummy pdf
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0/Kids[]>>endobj xref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n101\n%%EOF")

    # 4. Call FastAPI upload endpoint
    url = "http://127.0.0.1:8000/api/v1/pdf-ops/upload"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("dummy.pdf", open("dummy.pdf", "rb"), "application/pdf")}
    
    resp = requests.post(url, headers=headers, files=files)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)

    # cleanup
    service_client.auth.admin.delete_user(user_id)
    os.remove("dummy.pdf")

if __name__ == "__main__":
    test_upload()
