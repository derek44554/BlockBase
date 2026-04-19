import os
import hashlib
import secrets
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock NodeMeta before importing app components that use it
with patch('blocklink.utils.node_meta.NodeMeta') as mock_meta:
    mock_meta.return_value = {"ipfs_api": "http://localhost:5001/api/v0", "bid": "1234567890"}
    from main import app

client = TestClient(app)

@patch('requests.post')
def test_get_file_params_usage(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_post.return_value = mock_response

    cid = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"
    # The endpoint is registered via add_api(name="/ipfs", ...) which usually adds it to /ipfs
    # So it might be /ipfs/ipfs/{cid} if both have /ipfs
    response = client.get(f"/ipfs/ipfs/{cid}")
    if response.status_code == 404:
        response = client.get(f"/ipfs/{cid}")

    assert response.status_code == 200
    # Verify that requests.post was called with params instead of string interpolation
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:5001/api/v0/cat"
    assert kwargs['params'] == {"arg": cid}

@patch('requests.post')
def test_upload_file_security(mock_post):
    os.environ["IDENTITY"] = "test_secret"
    expected_password = hashlib.sha3_256("test_secret".encode() + "IPFS".encode('utf-8')).hexdigest()

    # Test successful upload with correct password
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Hash": "QmTest"}
    mock_post.return_value = mock_response

    with open("test_upload.txt", "w") as f:
        f.write("hello world")

    with open("test_upload.txt", "rb") as f:
        response = client.post(
            "/ipfs/ipfs/upload",
            data={"password": expected_password},
            files={"file": ("test_upload.txt", f)}
        )
        if response.status_code == 404:
            f.seek(0)
            response = client.post(
                "/ipfs/upload",
                data={"password": expected_password},
                files={"file": ("test_upload.txt", f)}
            )

    assert response.status_code == 200
    assert response.json() == {"cid": "QmTest"}

    # Verify secure password comparison (hard to test timing but we can verify it works)
    with open("test_upload.txt", "rb") as f:
        response = client.post(
            "/ipfs/ipfs/upload",
            data={"password": "wrong_password"},
            files={"file": ("test_upload.txt", f)}
        )
        if response.status_code == 404:
            f.seek(0)
            response = client.post(
                "/ipfs/upload",
                data={"password": "wrong_password"},
                files={"file": ("test_upload.txt", f)}
            )
    assert response.status_code == 403
    assert response.json()["detail"] == "密码错误"

    # Test generic error message on exception
    mock_post.side_effect = Exception("Internal DB error or similar")
    with open("test_upload.txt", "rb") as f:
        response = client.post(
            "/ipfs/ipfs/upload",
            data={"password": expected_password},
            files={"file": ("test_upload.txt", f)}
        )
        if response.status_code == 404:
            f.seek(0)
            response = client.post(
                "/ipfs/upload",
                data={"password": expected_password},
                files={"file": ("test_upload.txt", f)}
            )
    assert response.status_code == 500
    assert response.json()["detail"] == "上传失败"
    assert "Internal DB error" not in response.json()["detail"]

    if os.path.exists("test_upload.txt"):
        os.remove("test_upload.txt")

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
