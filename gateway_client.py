"""
Gateway API client for HyperSlop MCP Server
"""

import os
import json
import httpx
from typing import Dict, Any
from urllib.parse import urlparse, urlunparse

class GatewayConfig:
    def __init__(self, url: str, key: str, node: str):
        self.url = url
        self.key = key
        self.node = node

class GatewayClient:
    def __init__(self, config: GatewayConfig):
        self.config = config
        # Don't create the client in __init__, we'll create it per request
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': config.key
        }

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

    async def _make_request(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the gateway API"""
        try:
            # Convert localhost URLs to use 127.0.0.1
            url = self._fix_localhost_url(self.config.url)
            async with httpx.AsyncClient(headers=self.headers) as client:
                response = await client.post(url, json=action)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"Error": {"message": str(e)}}
        except Exception as e:
            return {"Error": {"message": f"Request failed: {str(e)}"}}

    # File System Operations
    async def read_directory(self, node: str, path: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "ReadPublicDir": {
                    "node": node,
                    "path": path
                }
            }
        }
        return await self._make_request(action)

    async def create_directory(self, node: str, path: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "CreateDir": {
                    "node": node,
                    "path": path
                }
            }
        }
        return await self._make_request(action)

    async def delete_directory(self, node: str, path: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "DeleteDir": {
                    "node": node,
                    "path": path
                }
            }
        }
        return await self._make_request(action)

    async def read_file(self, node: str, path: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "ReadFile": {
                    "node": node,
                    "path": path
                }
            }
        }
        return await self._make_request(action)

    async def create_file(self, node: str, path: str, content: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "CreateFile": {
                    "node": node,
                    "path": path,
                    "content": content
                }
            }
        }
        return await self._make_request(action)

    async def write_file(self, node: str, path: str, content: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "WriteFile": {
                    "node": node,
                    "path": path,
                    "content": content
                }
            }
        }
        return await self._make_request(action)

    async def delete_file(self, node: str, path: str) -> Dict[str, Any]:
        action = {
            "FileSystem": {
                "DeleteFile": {
                    "node": node,
                    "path": path
                }
            }
        }
        return await self._make_request(action)

    async def read_file_tree(self, node: str) -> Dict[str, Any]:
        """Read the entire file tree structure from a node.
        Returns only the structure (names, types, and paths) of files and directories,
        not the actual file contents."""
        action = {
            "FileSystem": {
                "ReadFileTree": {
                    "node": node
                }
            }
        }
        response = await self._make_request(action)
        
        # If we have a successful response with entries, strip the hyperslop path prefix
        if "ReadFileTree" in response and "entries" in response["ReadFileTree"]:
            prefix = "hyperslop:gliderlabs.os/public/"
            for entry in response["ReadFileTree"]["entries"]:
                if entry["path"].startswith(prefix):
                    entry["path"] = entry["path"][len(prefix):]
        
        return response

    async def read_api_key(self) -> Dict[str, Any]:
        action = {
            "System": {
                "ReadApiKey": None
            }
        }
        return await self._make_request(action) 