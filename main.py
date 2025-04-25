"""
Hyperslop MCP Server

This server provides access to the Hyperslop distributed file system network.
Each node in the network has its own filesystem, and nodes can access each other's files.
Your node name is configured in api.json and determines which filesystem you can modify.
Use the hyperslop_network_read tool with operation="get_node_name" to discover your node's name.
"""

import logging
import os
import json
from fastmcp import FastMCP, Context
from gateway_client import GatewayClient, GatewayConfig
from typing import Dict, Any, Literal

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
async def hyperslop_network_read(
    operation: Literal["get_node_name", "read_directory", "read_file", "read_file_tree"],
    node: str,
    path: str = "",
    ctx: Context = None
) -> Dict[str, Any]:
    """Read operations on the Hyperslop network.
    
    Args:
        operation: The type of read operation to perform:
            - get_node_name: Get your node's name as configured in api.json
            - read_directory: List contents of a directory
            - read_file: Read contents of a text file
            - read_file_tree: Read the entire file tree structure
        node: The name of the node to read from. You can read from any node in the network.
        path: The path to read from (not needed for get_node_name or read_file_tree)
        ctx: The context object for logging and progress reporting
    """
    if not gateway_client:
        logger.error("Gateway client not configured")
        return {"Error": {"message": "Gateway client not configured"}}

    if operation == "get_node_name":
        node_name = gateway_client.get_node()
        logger.info(f"Returning node name: {node_name}")
        return {"NodeName": node_name}
    
    elif operation == "read_directory":
        ctx.info(f"Reading directory: {path} on node {node}")
        return await gateway_client.read_directory(node, path)
    
    elif operation == "read_file":
        ctx.info(f"Reading file: {path} on node {node}")
        try:
            return await gateway_client.read_file(node, path)
        except Exception as e:
            return {"Error": {"message": str(e)}}
    
    elif operation == "read_file_tree":
        ctx.info(f"Reading file tree from node {node}")
        return await gateway_client.read_file_tree(node)
    
    return {"Error": {"message": f"Unknown operation: {operation}"}}

@mcp.tool()
async def hyperslop_network_write(
    operation: Literal["create_directory", "delete_directory", "write_file", "delete_file"],
    node: str,
    path: str,
    content: str = "",
    ctx: Context = None
) -> Dict[str, Any]:
    """Write operations on the Hyperslop network.
    
    Args:
        operation: The type of write operation to perform:
            - create_directory: Create a new directory
            - delete_directory: Delete a directory and its contents
            - write_file: Write content to a file (creates if doesn't exist)
            - delete_file: Delete a file
        node: Must match your node name from api.json. You can only write to your own node.
        path: The path to write to
        content: The text content to write (only for write_file operation)
        ctx: The context object for logging and progress reporting
    """
    # Debug logging
    logger.info("Received write operation request:")
    logger.info(f"Operation: {operation!r}")
    logger.info(f"Node: {node!r}")
    logger.info(f"Path: {path!r}")
    logger.info(f"Content: {content!r}")  # !r will show quotes and escapes
    logger.info(f"Content type: {type(content)}")
    logger.info(f"Content length: {len(content) if content is not None else 'None'}")

    if not gateway_client:
        logger.error("Gateway client not configured")
        return {"Error": {"message": "Gateway client not configured"}}

    # Verify node matches configured node for write operations
    if node != gateway_client.get_node():
        return {"Error": {"message": "You can only write to your own node"}}

    if operation == "create_directory":
        ctx.info(f"Creating directory: {path} on node {node}")
        return await gateway_client.create_directory(node, path)
    
    elif operation == "delete_directory":
        ctx.info(f"Deleting directory: {path} on node {node}")
        return await gateway_client.delete_directory(node, path)
    
    elif operation == "write_file":
        ctx.info(f"Writing to file: {path} on node {node}")
        if content is None or content.strip() == "":  # More explicit check
            logger.error("Content validation failed:")
            logger.error(f"Content is None: {content is None}")
            logger.error(f"Content stripped is empty: {content.strip() == '' if content is not None else 'N/A'}")
            return {"Error": {"message": "No file content provided"}}
        return await gateway_client.write_file(node, path, content)
    
    elif operation == "delete_file":
        ctx.info(f"Deleting file: {path} on node {node}")
        return await gateway_client.delete_file(node, path)
    
    return {"Error": {"message": f"Unknown operation: {operation}"}}
    