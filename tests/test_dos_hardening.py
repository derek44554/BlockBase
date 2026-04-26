import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
from types import ModuleType

# Comprehensive mocking of blocklink
def mock_package(name):
    m = ModuleType(name)
    m.__path__ = []
    sys.modules[name] = m
    return m

blocklink = mock_package('blocklink')
models = mock_package('blocklink.models')
blocklink.models = models

ins = mock_package('blocklink.models.ins')
models.ins = ins
sys.modules['blocklink.models.ins.ins_cert_factory'] = MagicMock()
sys.modules['blocklink.models.ins.ins_cert'] = MagicMock()
sys.modules['blocklink.models.ins.ins_open'] = MagicMock()

node = mock_package('blocklink.models.node')
models.node = node
sys.modules['blocklink.models.node.node'] = MagicMock()

routers = mock_package('blocklink.models.routers')
models.routers = routers
sys.modules['blocklink.models.routers.route_block_app'] = MagicMock()
sys.modules['blocklink.models.routers.route_block'] = MagicMock()

utils = mock_package('blocklink.utils')
blocklink.utils = utils
sys.modules['blocklink.utils.block_model'] = MagicMock()
sys.modules['blocklink.utils.ins_except'] = MagicMock()
sys.modules['blocklink.utils.send'] = MagicMock()
node_meta = mock_package('blocklink.utils.node_meta')
utils.node_meta = node_meta
node_meta.NodeMeta = MagicMock(return_value={"ipfs_api": "http://localhost:5001/api/v0"})

# Mocking apps.block to avoid DB issues
mock_package('apps.block')
mock_package('apps.block.utils')
sys.modules['apps.block.utils.block'] = MagicMock()
sys.modules['apps.block.utils.db_block'] = MagicMock()

import apps.ipfs.utils.ipfs_api as ipfs_api_module

class TestDoSHardening(unittest.IsolatedAsyncioTestCase):
    @patch('apps.ipfs.utils.ipfs_api.requests.post')
    def test_ipfs_api_add_timeout(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'Hash': 'test_cid'}

        with open('dummy.txt', 'w') as f:
            f.write('test')

        try:
            ipfs_api_module.add_file_to_ipfs('dummy.txt')
        except:
            pass
        finally:
            if os.path.exists('dummy.txt'):
                os.remove('dummy.txt')

        args, kwargs = mock_post.call_args
        self.assertIn('timeout', kwargs, "timeout missing in add_file_to_ipfs")

    @patch('apps.ipfs.utils.ipfs_api.requests.post')
    def test_get_file_chunk_streaming(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"some data"
        mock_post.return_value = mock_response

        try:
            ipfs_api_module.get_file_chunk_from_ipfs('test_cid')
        except:
            pass

        args, kwargs = mock_post.call_args
        self.assertTrue(kwargs.get('stream'), "stream=True missing in get_file_chunk_from_ipfs")
        self.assertIn('timeout', kwargs, "timeout missing in get_file_chunk_from_ipfs")

    @patch('apps.ipfs.routers.ipfs.requests.post')
    async def test_router_get_file_streaming(self, mock_post):
        from apps.ipfs.routers.ipfs import get_file

        mock_response = MagicMock()
        mock_response.status_code = 200
        # iter_content is needed if using StreamingResponse
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_post.return_value = mock_response

        await get_file('test_cid')

        args, kwargs = mock_post.call_args
        self.assertTrue(kwargs.get('stream'), "stream=True missing in router get_file")
        self.assertIn('timeout', kwargs, "timeout missing in router get_file")

if __name__ == '__main__':
    unittest.main()
