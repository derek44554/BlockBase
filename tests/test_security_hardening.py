import unittest
from unittest.mock import patch, MagicMock
import os
import hashlib
import asyncio

# Mock NodeMeta before importing anything that uses it
with patch('blocklink.utils.node_meta.NodeMeta') as mock_node_meta:
    mock_node_meta.return_value = {"ipfs_api": "http://localhost:5001/api/v0", "bid": "12345678901234567890123456789012"}
    from apps.ipfs.routers.ipfs import get_file, upload_file
    import apps.ipfs.utils.ipfs_api as ipfs_api_utils

class TestSecurityHardening(unittest.TestCase):

    @patch('apps.ipfs.routers.ipfs.requests.post')
    def test_get_file_no_parameter_injection(self, mock_post):
        cid = "QmXoypizj2Madv6S2w2LAmrxSokhsBZW1Y6ZQKM2id6uvf&other=param"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"data"]
        mock_post.return_value = mock_response

        # Run the async function
        asyncio.run(get_file(cid))

        # Check if CID was passed via params
        called_kwargs = mock_post.call_args[1]
        self.assertIn('params', called_kwargs)
        self.assertEqual(called_kwargs['params'], {'arg': cid})

    @patch('apps.ipfs.utils.ipfs_api.requests.post')
    def test_ipfs_utils_no_parameter_injection(self, mock_post):
        cid = "QmXoypizj2Madv6S2w2LAmrxSokhsBZW1Y6ZQKM2id6uvf&other=param"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        ipfs_api_utils.pin_cid(cid)

        called_kwargs = mock_post.call_args[1]
        self.assertIn('params', called_kwargs)
        self.assertEqual(called_kwargs['params'], {'arg': cid})

    def test_password_comparison_uses_compare_digest(self):
        import inspect
        source = inspect.getsource(upload_file)
        self.assertIn("secrets.compare_digest", source, "Should use secrets.compare_digest for password comparison")

    @patch('apps.ipfs.routers.ipfs.os.getenv')
    @patch('apps.ipfs.routers.ipfs.add_file_to_ipfs')
    def test_exception_masking(self, mock_add_file, mock_getenv):
        mock_getenv.return_value = "secret"
        mock_add_file.side_effect = Exception("Sensitive Internal Error")

        # Mock file and other dependencies for upload_file
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.read = MagicMock(return_value=asyncio.Future())
        mock_file.read.return_value.set_result(b"content")

        # Mock password verification
        expected_password = hashlib.sha3_256("secret".encode()+"IPFS".encode('utf-8')).hexdigest()

        with self.assertRaises(Exception) as cm:
            asyncio.run(upload_file(password=expected_password, file=mock_file))

        from fastapi import HTTPException
        if isinstance(cm.exception, HTTPException):
            self.assertEqual(cm.exception.detail, "上传失败: 服务器内部错误")
            self.assertNotIn("Sensitive Internal Error", cm.exception.detail)

if __name__ == "__main__":
    unittest.main()
