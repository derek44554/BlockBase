import hashlib
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.ipfs.routers.ipfs import ipfs_fast_api


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(ipfs_fast_api)
    return TestClient(app)


@patch("apps.ipfs.routers.ipfs.add_file_to_ipfs")
@patch("apps.ipfs.routers.ipfs.pin_cid")
@patch.dict(os.environ, {"IDENTITY": "test_password"})
def test_upload_file_generic_error(mock_pin_cid, mock_add_file_to_ipfs, client):
    # Setup: mock add_file_to_ipfs to raise an Exception
    mock_add_file_to_ipfs.side_effect = Exception("Internal database error")

    # Correct password
    password = hashlib.sha3_256("test_password".encode() + "IPFS".encode('utf-8')).hexdigest()

    # Request
    response = client.post(
        "/upload",
        data={"password": password},
        files={"file": ("test.txt", b"test content")}
    )

    # Verification
    assert response.status_code == 500
    assert response.json()["detail"] == "上传失败"
    # Ensure the detailed exception is not in the response
    assert "Internal database error" not in response.json()["detail"]


@patch.dict(os.environ, {"IDENTITY": "test_password"})
def test_upload_file_invalid_password(client):
    # Invalid password
    password = "wrong_password"

    # Request
    response = client.post(
        "/upload",
        data={"password": password},
        files={"file": ("test.txt", b"test content")}
    )

    # Verification
    assert response.status_code == 403
    assert response.json()["detail"] == "密码错误"
