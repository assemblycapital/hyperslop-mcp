# Hyperslop MCP Server

A basic MCP (Model Context Protocol) server implementation using FastMCP that provides access to a hyperslop gateway API.

## Features

- Gateway API Integration:
  - Text File Operations (read, write, delete text files)
  - Directory Operations (create, read, delete directories)
  - File Tree Operations (read entire file structure)
  - Configurable via api.json file
- Basic MCP tools and resources:
  - Text file operations through Gateway API
  - Directory operations through Gateway API
  - File tree operations through Gateway API
- Logging for all operations
- Progress reporting for long-running operations

## Installation

1. Clone this repository:
  ```bash
  git clone https://github.com/your-username/hyperslop-mcp.git
  cd hyperslop-mcp
  ```

2. Create and activate a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Unix/macOS
  # or
  .\venv\Scripts\activate  # On Windows
  ```

3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

4. Install FastMCP using uv (required for deploying servers):
  ```bash
  # First install uv if you don't have it
  # On macOS:
  brew install uv
  # On other platforms, follow instructions at https://github.com/astral-sh/uv

  # Then install FastMCP
  uv pip install fastmcp
  ```

5. Configure the Gateway API:
   - Open the HyperSlop app on the Hyperware network
   - Click the "Copy API" button in the top right corner
   - Create an `api.json` file in the project root directory
   - Paste the copied API configuration into the file

6. Install the MCP server:
  ```bash
  fastmcp install main.py
  ```

7. The next time you open Claude Desktop, the HyperSlop MCP will be available.

## Running the Server

### Development Mode (For Testing)

Run the server in development mode with:
  ```bash
  fastmcp dev main.py
  ```

This launches the MCP Inspector interface where you can:
- Test your tools and resources interactively
- See detailed logs and error messages
- Monitor server performance

## Available Tools

The server provides two main tools that handle all file system operations:

### 1. hyperslop_network_read

Read operations on the Hyperslop network. Available operations:

- `get_node_name`: Get your node's name as configured in api.json
- `read_directory`: List contents of a directory on any node
- `read_file`: Read contents of a text file from any node
- `read_file_tree`: Read the entire file tree structure from any node

Example request:
```json
{
  "operation": "read_file",
  "node": "fake.os",
  "path": "example.txt"
}
```

### 2. hyperslop_network_write

Write operations on the Hyperslop network. Available operations:

- `create_directory`: Create a new directory on your node
- `delete_directory`: Delete a directory and its contents from your node
- `write_file`: Write content to a file (creates if doesn't exist)
- `delete_file`: Delete a file from your node

Example request:
```json
{
  "operation": "write_file",
  "node": "fake.os",
  "path": "example.txt",
  "content": "Hello, world!"
}
```

Note: Write operations can only be performed on your own node (as configured in api.json).

## Limitations

- This MCP server only handles text files. For binary files or large files, use the HyperSlop app directly.
- All file operations are performed through the Gateway API using the credentials in api.json.