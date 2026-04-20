import pytest
import os
import hashlib
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from apps.ipfs.routers.ipfs import ipfs_fast_api
from apps.ipfs.utils.ipfs_api import pin_cid, unpin_cid

# Setup environment for tests
os.environ["IDENTITY"] = "testpassword"

# Create a proper FastAPI app for testing
app = FastAPI()
app.include_router(ipfs_fast_api)

client = TestClient(app)

@patch("apps.ipfs.routers.ipfs.requests.post")
def test_get_file_parameter_injection_fixed(mock_post):
    """Verify if the CID parameter is protected from URL injection."""
    mock_post.return_value = MagicMock(status_code=200)
    mock_post.return_value.iter_content.return_value = [b"data"]

    cid = "valid_cid&arg=malicious"
    client.get(f"/{cid}")

    args, kwargs = mock_post.call_args
    url = args[0]
    params = kwargs.get('params', {})

    # Injection should NOT be in the URL as a raw string
    assert f"arg={cid}" not in url
    # It should be in params and correctly handled by requests
    assert params.get('arg') == cid

@patch("apps.ipfs.routers.ipfs.requests.post")
def test_upload_file_error_leakage_fixed(mock_post):
    """Verify if internal exception details are NOT leaked in error responses."""
    mock_post.side_effect = Exception("Sensitive Internal Error Details")

    password = hashlib.sha3_256("testpassword".encode() + "IPFS".encode('utf-8')).hexdigest()

    files = {'file': ('test.txt', b'hello world')}
    data = {'password': password}

    response = client.post("/upload", data=data, files=files)

    assert response.status_code == 500
    # The response should NOT contain the sensitive details
    assert "Sensitive Internal Error Details" not in response.json()["detail"]
    assert "服务器内部错误" in response.json()["detail"]

@patch("apps.ipfs.utils.ipfs_api.requests.post")
def test_ipfs_api_utils_injection_fixed(mock_post):
    """Verify if IPFS utility functions are protected from URL injection."""
    mock_post.return_value = MagicMock(status_code=200)

    malicious_cid = "cid&arg=attack"

    # Test pin_cid
    pin_cid(malicious_cid)
    args, kwargs = mock_post.call_args
    assert f"arg={malicious_cid}" not in args[0]
    assert kwargs.get('params', {}).get('arg') == malicious_cid

    # Test unpin_cid
    unpin_cid(malicious_cid)
    args, kwargs = mock_post.call_args
    assert f"arg={malicious_cid}" not in args[0]
    assert kwargs.get('params', {}).get('arg') == malicious_cid

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
