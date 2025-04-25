"""
Gateway API client for HyperSlop MCP Server
"""

import os
import json
import httpx
from typing import Dict, Any, Union, Tuple
from urllib.parse import urlparse, urlunparse

class GatewayConfig:
    def __init__(self, url: str, key: str, node: str):
        self.url = url
        self.key = key
        self.node = node

class GatewayClient:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.headers = {
            'X-API-Key': config.key
        }
        # Parse the base URL to construct API endpoints
        base_url = config.url.rstrip('/')
        self.rpc_url = f"{base_url}/rpc"
        self.read_url = f"{base_url}/read"

    def get_node(self) -> str:
        """Get the configured node name"""
        return self.config.node

    def _fix_localhost_url(self, url: str) -> str:
        """Convert any localhost subdomain to 127.0.0.1"""
        parsed = urlparse(url)
        if '.localhost' in parsed.netloc or parsed.netloc == 'localhost':
            # Keep the port if it exists
            port = f":{parsed.port}" if parsed.port else ""
            # Replace the hostname with 127.0.0.1
            parsed = parsed._replace(netloc=f"127.0.0.1{port}")
        return urlunparse(parsed)

    async def _make_rpc_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the gateway RPC API endpoint"""
        try:
            url = self._fix_localhost_url(self.rpc_url)
            headers = {**self.headers, 'Content-Type': 'application/json'}
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.post(url, json=request)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"Error": {"message": str(e)}}
        except Exception as e:
            return {"Error": {"message": f"Request failed: {str(e)}"}}

    async def _make_read_request(self, node: str, path: str) -> Dict[str, Any]:
        """Make a request to the gateway read API endpoint.
        Only returns text content, returns an error for non-text files."""
        try:
            url = self._fix_localhost_url(f"{self.read_url}/{node}/{path}")
            async with httpx.AsyncClient(headers=self.headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                mime_type = response.headers.get('Content-Type', 'text/plain')
                
                # Only handle text/* mime types
                if not mime_type.startswith('text/'):
                    return {"Error": {"message": f"File is not a text file (mime type: {mime_type})"}}
                
                content = response.text
                return {"ReadFile": {"content": content, "mime_type": mime_type}}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"Error": {"message": f"File not found: {path}"}}
            return {"Error": {"message": str(e)}}
        except Exception as e:
            return {"Error": {"message": f"Request failed: {str(e)}"}}

    # File System Operations
    async def read_directory(self, node: str, path: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "ReadPublicDir",
                "path": path
            }
        }
        return await self._make_rpc_request(request)

    async def create_directory(self, node: str, path: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "CreateDir",
                "path": path
            }
        }
        return await self._make_rpc_request(request)

    async def delete_directory(self, node: str, path: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "DeleteDir",
                "path": path
            }
        }
        return await self._make_rpc_request(request)

    async def read_file(self, node: str, path: str) -> Dict[str, Any]:
        """Read a text file's contents using the read endpoint"""
        return await self._make_read_request(node, path)

    async def create_file(self, node: str, path: str, content: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "CreateFile",
                "path": path,
                "content": content
            }
        }
        return await self._make_rpc_request(request)

    async def write_file(self, node: str, path: str, content: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "WriteFile",
                "path": path,
                "content": content
            }
        }
        return await self._make_rpc_request(request)

    async def delete_file(self, node: str, path: str) -> Dict[str, Any]:
        request = {
            "node": node,
            "request": {
                "request_type": "DeleteFile",
                "path": path
            }
        }
        return await self._make_rpc_request(request)

    async def read_file_tree(self, node: str) -> Dict[str, Any]:
        """Read the entire file tree structure from a node.
        Returns only the structure (names, types, and paths) of files and directories,
        not the actual file contents."""
        request = {
            "node": node,
            "request": {
                "request_type": "ReadFileTree",
                "path": ""
            }
        }
        return await self._make_rpc_request(request)

    async def read_api_key(self) -> Dict[str, Any]:
        action = {
            "System": {
                "ReadApiKey": None
            }
        }
        return await self._make_rpc_request(action)
