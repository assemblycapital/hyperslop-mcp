"""
Hyperslop MCP Server

This server provides access to the Hyperslop distributed file system network.
Each node in the network has its own filesystem, and nodes can access each other's files.
Your node name is configured in api.json and determines which filesystem you can modify.
Use the get_our_node_name tool to discover your node's name.
"""

import logging
import os
import json
from fastmcp import FastMCP, Context
from gateway_client import GatewayClient, GatewayConfig

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create server
mcp = FastMCP("Hyperslop Server")

# Initialize empty gateway client
gateway_client = None

# Get the absolute path to api.json based on the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
api_json_path = os.path.join(script_dir, 'api.json')

# Try to load configuration from api.json
try:
    logger.info(f"Attempting to load configuration from {api_json_path}")
    with open(api_json_path, 'r') as f:
        config = json.load(f)
        logger.info(f"Loaded config: {config}")
        gateway_client = GatewayClient(GatewayConfig(
            url=config['url'],
            key=config['key'],
            node=config['node']
        ))
        logger.info(f"Successfully initialized gateway client with node: {gateway_client.get_node()}")
except FileNotFoundError:
    logger.error(f"api.json not found at {api_json_path}")
    logger.error(f"Current directory: {os.getcwd()}")
    logger.error(f"Directory contents: {os.listdir('.')}")
except json.JSONDecodeError as e:
    logger.error(f"api.json contains invalid JSON: {e}")
except Exception as e:
    logger.error(f"Error loading configuration from api.json: {e}")
    logger.error(f"Error type: {type(e)}")
    logger.error(f"Error details: {str(e)}")

# Log startup information
logger.info("Starting Hyperslop MCP Server")
logger.info("Default MCP port is 8815 (standard MCP port)")
logger.info("Access the server at: http://localhost:8815")

@mcp.tool()
def get_our_node_name() -> str:
    """Get your node's name as configured in api.json.
    This is your identity in the Hyperslop network and determines which filesystem you can modify."""
    if not gateway_client:
        logger.error("Gateway client not configured - get_our_node_name called before initialization")
        return "No node configured"
    node_name = gateway_client.get_node()
    logger.info(f"Returning node name: {node_name}")
    return node_name

# File System Operations
@mcp.tool()
async def read_directory(node: str, path: str, ctx: Context) -> dict:
    """List contents of a directory on any node in the Hyperslop network.
    
    Args:
        node: The name of the node to read from. You can read from any node in the network.
              Use get_our_node_name() to get your node's name.
        path: The directory path to list contents from.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - read_directory called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    ctx.info(f"Reading directory: {path} on node {node}")
    return await gateway_client.read_directory(node, path)

@mcp.tool()
async def create_directory(node: str, path: str, ctx: Context) -> dict:
    """Create a new directory on your node.
    
    Args:
        node: Must match your node name from api.json. You can only create directories on your own node.
              Use get_our_node_name() to get your node's name.
        path: The directory path to create.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - create_directory called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only create directories on your own node"}}
    ctx.info(f"Creating directory: {path} on node {node}")
    return await gateway_client.create_directory(node, path)

@mcp.tool()
async def delete_directory(node: str, path: str, ctx: Context) -> dict:
    """Delete a directory and its contents from your node.
    
    Args:
        node: Must match your node name from api.json. You can only delete directories on your own node.
              Use get_our_node_name() to get your node's name.
        path: The directory path to delete.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - delete_directory called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only delete directories on your own node"}}
    ctx.info(f"Deleting directory: {path} on node {node}")
    return await gateway_client.delete_directory(node, path)

@mcp.tool()
async def read_file(node: str, path: str, ctx: Context) -> dict:
    """Read contents of a file from any node in the Hyperslop network.
    
    Args:
        node: The name of the node to read from. You can read from any node in the network.
              Use get_our_node_name() to get your node's name.
        path: The file path to read.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - read_file called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    ctx.info(f"Reading file: {path} on node {node}")
    return await gateway_client.read_file(node, path)

@mcp.tool()
async def create_file(node: str, path: str, content: str, ctx: Context) -> dict:
    """Create a new file with content on your node.
    
    Args:
        node: Must match your node name from api.json. You can only create files on your own node.
              Use get_our_node_name() to get your node's name.
        path: The file path to create.
        content: The content to write to the new file.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - create_file called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only create files on your own node"}}
    ctx.info(f"Creating file: {path} on node {node}")
    return await gateway_client.create_file(node, path, content)

@mcp.tool()
async def write_file(node: str, path: str, content: str, ctx: Context) -> dict:
    """Write content to an existing file on your node.
    
    Args:
        node: Must match your node name from api.json. You can only write to files on your own node.
              Use get_our_node_name() to get your node's name.
        path: The file path to write to.
        content: The content to write to the file.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - write_file called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only write to files on your own node"}}
    ctx.info(f"Writing to file: {path} on node {node}")
    return await gateway_client.write_file(node, path, content)

@mcp.tool()
async def delete_file(node: str, path: str, ctx: Context) -> dict:
    """Delete a file from your node.
    
    Args:
        node: Must match your node name from api.json. You can only delete files on your own node.
              Use get_our_node_name() to get your node's name.
        path: The file path to delete.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - delete_file called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only delete files on your own node"}}
    ctx.info(f"Deleting file: {path} on node {node}")
    return await gateway_client.delete_file(node, path)

@mcp.tool()
async def read_file_tree(node: str, ctx: Context) -> dict:
    """Read the file tree structure from any node in the Hyperslop network.
    This returns only the structure (names, types, and paths) of files and directories,
    not the actual file contents.
    
    Args:
        node: The name of the node to read from. You can read from any node in the network.
              Use get_our_node_name() to get your node's name.
    """
    if not gateway_client:
        logger.error("Gateway client not configured - read_file_tree called before initialization")
        return {"Error": {"message": "Gateway client not configured"}}
    ctx.info(f"Reading file tree from node {node}")
    return await gateway_client.read_file_tree(node) 