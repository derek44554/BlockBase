import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import os

# Mocking NodeMeta before importing anything that uses it
with patch('blocklink.utils.node_meta.NodeMeta') as mock_node_meta:
    mock_node_meta.return_value = {"ipfs_api": "http://localhost:5001/api/v0"}

    # Now we can import the router
    from apps.ipfs.routers.ipfs import get_file, upload_file
    import apps.ipfs.utils.ipfs_api as ipfs_utils

class TestSecurity(unittest.IsolatedAsyncioTestCase):
    @patch('requests.post')
    async def test_get_file_url_injection(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"data"]
        mock_post.return_value = mock_response

        cid = "test_cid&other=value"
        await get_file(cid)

        # Check if the URL and params were passed correctly
        called_url = mock_post.call_args[0][0]
        called_params = mock_post.call_args[1].get('params')

        self.assertEqual(called_url, "http://localhost:5001/api/v0/cat")
        self.assertEqual(called_params, {"arg": "test_cid&other=value"})

    @patch('apps.ipfs.routers.ipfs.add_file_to_ipfs')
    @patch('os.getenv')
    async def test_upload_file_generic_error(self, mock_getenv, mock_add):
        mock_getenv.return_value = "secret"
        mock_add.side_effect = Exception("Detailed internal error")

        # Mock file
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.read.return_value = b"content"

        import hashlib
        password = hashlib.sha3_256("secret".encode()+"IPFS".encode('utf-8')).hexdigest()

        try:
            await upload_file(password=password, file=mock_file)
        except HTTPException as e:
            self.assertEqual(e.status_code, 500)
            self.assertEqual(e.detail, "上传失败")
            self.assertNotIn("Detailed internal error", e.detail)

if __name__ == "__main__":
    unittest.main()
