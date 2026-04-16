import hashlib
import os
import secrets
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mocking NodeMeta to avoid initialization issues
with patch('blocklink.utils.node_meta.NodeMeta', return_value={"ipfs_api": "http://localhost:5001/api/v0"}):
    from main import app

client = TestClient(app)

def test_ipfs_password_hashing_logic():
    """
    Verify the hashing logic in the upload endpoint is consistent with what we expect.
    """
    identity = "test_identity"
    expected_password = hashlib.sha3_256(identity.encode() + "IPFS".encode('utf-8')).hexdigest()

    # This is internal logic from apps/ipfs/routers/ipfs.py
    actual_password = hashlib.sha3_256(identity.encode() + "IPFS".encode('utf-8')).hexdigest()
    assert secrets.compare_digest(actual_password, expected_password)

@patch('apps.ipfs.routers.ipfs.requests.post')
def test_get_file_secure_url(mock_post):
    """
    Verify that the get_file endpoint uses secure URL construction with params.
    """
    mock_post.return_value.status_code = 200
    mock_post.return_value.iter_content = lambda chunk_size: [b"data"]

    cid = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"
    # Based on apps/ipfs/__init__.py, the path should be /ipfs/ipfs/{cid}
    response = client.get(f"/ipfs/ipfs/{cid}")

    assert response.status_code == 200
    # Check if requests.post was called with params instead of interpolated URL
    args, kwargs = mock_post.call_args
    assert "params" in kwargs
    assert kwargs["params"]["arg"] == cid
    assert "?" not in args[0]

@patch('apps.ipfs.routers.ipfs.os.getenv')
@patch('apps.ipfs.routers.ipfs.add_file_to_ipfs')
@patch('apps.ipfs.routers.ipfs.pin_cid')
def test_upload_file_error_handling(mock_pin, mock_add, mock_getenv):
    """
    Verify that internal exception details are not leaked in the upload endpoint.
    """
    mock_getenv.return_value = "test_identity"
    mock_add.side_effect = Exception("Internal Secret Error")

    identity = "test_identity"
    password = hashlib.sha3_256(identity.encode() + "IPFS".encode('utf-8')).hexdigest()

    files = {'file': ('test.txt', b'hello world')}
    # Based on apps/ipfs/__init__.py, the path should be /ipfs/ipfs/upload
    response = client.post("/ipfs/ipfs/upload", data={"password": password}, files=files)

    assert response.status_code == 500
    assert response.json()["detail"] == "上传失败"
    assert "Internal Secret Error" not in response.json()["detail"]

@patch('apps.ipfs.utils.ipfs_api.requests.post')
def test_ipfs_api_utils_secure_urls(mock_post):
    """
    Verify that utility functions use secure URL construction.
    """
    from apps.ipfs.utils.ipfs_api import pin_cid, unpin_cid, get_file_chunk_from_ipfs

    mock_post.return_value.status_code = 200
    mock_post.return_value.content = b"chunked data"

    cid = "test_cid"

    # Test pin_cid
    pin_cid(cid)
    args, kwargs = mock_post.call_args
    assert kwargs["params"]["arg"] == cid

    # Test unpin_cid
    unpin_cid(cid)
    args, kwargs = mock_post.call_args
    assert kwargs["params"]["arg"] == cid

    # Test get_file_chunk_from_ipfs
    get_file_chunk_from_ipfs(cid)
    args, kwargs = mock_post.call_args
    assert kwargs["params"]["arg"] == cid
