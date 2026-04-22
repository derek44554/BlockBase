import os
import hashlib
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import secrets

# Set IDENTITY for password derivation
os.environ["IDENTITY"] = "test_identity"

# We need to mock NodeMeta BEFORE importing anything that uses it if it's not already set up.
# But we already set up node.yml etc.

from apps.ipfs.routers.ipfs import ipfs_fast_api
from fastapi import FastAPI

app = FastAPI()
app.include_router(ipfs_fast_api)
client = TestClient(app)

def test_password_verification_logic():
    # Verify we can calculate the correct password
    ipfs_password = "test_identity"
    correct_password = hashlib.sha3_256(ipfs_password.encode()+"IPFS".encode('utf-8')).hexdigest()

    with patch("apps.ipfs.routers.ipfs.add_file_to_ipfs") as mock_add:
        mock_add.return_value = "QmHash"
        with patch("apps.ipfs.routers.ipfs.pin_cid") as mock_pin:
            response = client.post("/upload", data={"password": correct_password}, files={"file": ("test.txt", b"content")})
            assert response.status_code == 200
            assert response.json() == {"cid": "QmHash"}

    response = client.post("/upload", data={"password": "wrong"}, files={"file": ("test.txt", b"content")})
    assert response.status_code == 403
    assert response.json()["detail"] == "密码错误"

def test_get_file_info_leakage():
    with patch("apps.ipfs.routers.ipfs.requests.post") as mock_post:
        mock_post.side_effect = Exception("Sensitive internal error details")
        response = client.get("/some_cid")
        # Currently it raises Exception which results in 500 and leaks the message in some environments,
        # or just 500 if FastAPI handles it.
        # Actually in our previous run it raised the exception and TestClient didn't catch it for us to see the response.
        # We want it to be a 500 with generic message.
        assert response.status_code == 500
        assert "Sensitive" not in response.text

def test_upload_file_info_leakage():
    ipfs_password = "test_identity"
    pwd = hashlib.sha3_256(ipfs_password.encode()+"IPFS".encode('utf-8')).hexdigest()

    with patch("apps.ipfs.routers.ipfs.add_file_to_ipfs") as mock_add:
        mock_add.side_effect = Exception("Sensitive path: /etc/passwd")
        response = client.post("/upload", data={"password": pwd}, files={"file": ("test.txt", b"content")})
        assert response.status_code == 500
        assert "Sensitive path" not in response.json()["detail"]

def test_url_manipulation_prevention():
    with patch("apps.ipfs.routers.ipfs.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"data"]
        mock_post.return_value = mock_response

        cid = "Qm123&arg=malicious"
        client.get(f"/{cid}")

        # Check how requests.post was called
        # If it was f"{ipfs_api}/cat?arg={cid}", it's vulnerable.
        args, kwargs = mock_post.call_args
        called_url = args[0]
        assert "&arg=malicious" not in called_url or "params=" in str(mock_post.call_args)

if __name__ == "__main__":
    # Run tests manually
    try:
        test_password_verification_logic()
        print("test_password_verification_logic passed")
    except Exception as e:
        print(f"test_password_verification_logic failed: {e}")

    try:
        test_get_file_info_leakage()
        print("test_get_file_info_leakage passed")
    except Exception as e:
        print(f"test_get_file_info_leakage failed: {e}")

    try:
        test_upload_file_info_leakage()
        print("test_upload_file_info_leakage passed")
    except Exception as e:
        print(f"test_upload_file_info_leakage failed: {e}")

    try:
        test_url_manipulation_prevention()
        print("test_url_manipulation_prevention passed")
    except Exception as e:
        print(f"test_url_manipulation_prevention failed: {e}")
