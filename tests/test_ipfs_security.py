import os
import hashlib
import secrets
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Set up environment variables for blocklink before importing app
os.environ["IDENTITY"] = "test_password"

# Mock blocklink.utils.node_meta.NodeMeta to avoid needing real config files
with patch("blocklink.utils.node_meta.NodeMeta") as mock_meta:
    mock_meta.return_value = {"ipfs_api": "http://mock-ipfs:5001/api/v0", "bid": "0123456789abcdef0123456789abcdef"}
    from main import app

client = TestClient(app)

def test_get_file_params_security():
    """
    Test that get_file uses params for CID, preventing URL manipulation.
    We mock requests.post and check how it's called.
    """
    with patch("apps.ipfs.routers.ipfs.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_post.return_value = mock_response

        # Corrected URL path: apps/ipfs/__init__.py adds it with name="/ipfs"
        # and ipfs_app itself is mounted at /ipfs.
        # So it might be /ipfs/ipfs/{cid}
        response = client.get("/ipfs/ipfs/QmTestCID")

        assert response.status_code == 200
        # Check that it was called with params instead of just in the URL
        args, kwargs = mock_post.call_args
        assert kwargs["params"] == {"arg": "QmTestCID"}

def test_upload_file_security_timing_attack():
    """
    Test that upload_file verifies the password.
    Note: We can't easily test for timing attacks with unit tests,
    but we can verify that secrets.compare_digest is called if we mock it.
    """
    # Calculate the expected hashed password
    expected_password = hashlib.sha3_256("test_password".encode() + "IPFS".encode('utf-8')).hexdigest()

    with patch("apps.ipfs.routers.ipfs.secrets.compare_digest", wraps=secrets.compare_digest) as mock_compare:
        # Test with correct password
        with patch("apps.ipfs.routers.ipfs.add_file_to_ipfs") as mock_add, \
             patch("apps.ipfs.routers.ipfs.pin_cid") as mock_pin:
            mock_add.return_value = "QmNewCID"

            response = client.post(
                "/ipfs/ipfs/upload",
                data={"password": expected_password},
                files={"file": ("test.txt", b"content")}
            )
            assert response.status_code == 200
            assert mock_compare.called

        # Test with wrong password
        response = client.post(
            "/ipfs/ipfs/upload",
            data={"password": "wrong_password"},
            files={"file": ("test.txt", b"content")}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "密码错误"

def test_upload_file_security_no_exception_leak():
    """
    Test that upload_file doesn't leak internal exceptions.
    """
    expected_password = hashlib.sha3_256("test_password".encode() + "IPFS".encode('utf-8')).hexdigest()

    with patch("apps.ipfs.routers.ipfs.add_file_to_ipfs", side_effect=Exception("Database connection failed!")):
        response = client.post(
            "/ipfs/ipfs/upload",
            data={"password": expected_password},
            files={"file": ("test.txt", b"content")}
        )
        assert response.status_code == 500
        # Should NOT contain the internal exception message
        assert "Database connection failed!" not in response.json()["detail"]
        assert response.json()["detail"] == "上传失败"

def test_ipfs_api_utils_params_security():
    """
    Test that utility functions in apps/ipfs/utils/ipfs_api.py use params.
    """
    from apps.ipfs.utils.ipfs_api import pin_cid, unpin_cid, add_file_to_ipfs

    with patch("apps.ipfs.utils.ipfs_api.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Test pin_cid
        pin_cid("QmTestCID")
        args, kwargs = mock_post.call_args
        assert kwargs["params"] == {"arg": "QmTestCID"}

        # Test unpin_cid
        unpin_cid("QmTestCID")
        args, kwargs = mock_post.call_args
        assert kwargs["params"] == {"arg": "QmTestCID"}

        # Test add_file_to_ipfs
        mock_response.json.return_value = {"Hash": "QmNewCID"}
        with patch("builtins.open", MagicMock()):
            add_file_to_ipfs("fake_path")
            args, kwargs = mock_post.call_args
            assert kwargs["params"] == {"pin": "true"}
