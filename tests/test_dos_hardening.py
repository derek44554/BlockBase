import unittest
from unittest.mock import patch, MagicMock
import requests
from fastapi import HTTPException

# Mocking NodeMeta before importing
with patch('blocklink.utils.node_meta.NodeMeta') as mock_node_meta:
    mock_node_meta.return_value = {"ipfs_api": "http://localhost:5001/api/v0"}
    from apps.ipfs.utils.ipfs_api import get_file_chunk_from_ipfs

class TestDosHardening(unittest.IsolatedAsyncioTestCase):
    @patch('requests.post')
    async def test_get_file_chunk_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(HTTPException) as cm:
            get_file_chunk_from_ipfs("some_cid")

        self.assertEqual(cm.exception.status_code, 504)
        self.assertEqual(cm.exception.detail, "IPFS cat timeout")

    @patch('requests.post')
    async def test_get_file_chunk_streaming(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': '20'}
        # Return a generator for iter_content
        mock_response.iter_content.return_value = iter([b"1234567890", b"1234567890"])
        mock_post.return_value = mock_response

        stream, total_count = get_file_chunk_from_ipfs("some_cid", chunk_size=10)

        self.assertEqual(total_count, 2)
        chunks = list(stream)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], b"1234567890")

        # Verify requests.post was called with stream=True and timeout
        args, kwargs = mock_post.call_args
        self.assertTrue(kwargs.get('stream'))
        self.assertEqual(kwargs.get('timeout'), 30)

if __name__ == "__main__":
    unittest.main()
