"""
Example: MCP Client Implementation Pattern

This example demonstrates the standard pattern for implementing MCP clients
in the GraphMCP framework.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from clients.base import BaseMCPClient, MCPConnectionError, MCPToolError

logger = logging.getLogger(__name__)


class ExampleMCPClient(BaseMCPClient):
    """
    Example MCP client implementation following GraphMCP patterns.

    Key Patterns:
    1. SERVER_NAME class attribute (required)
    2. Async context manager support
    3. Structured error handling
    4. Comprehensive logging
    5. Health check implementation
    """

    # Required: Define the server name
    SERVER_NAME = "example_server"

    def __init__(self, config_path: str | Path):
        """
        Initialize the client.

        Args:
            config_path: Path to MCP configuration file
        """
        super().__init__(config_path)
        self._connected = False
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    async def __aenter__(self) -> "ExampleMCPClient":
        """
        Async context manager entry.

        Returns:
            Self for context manager usage
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.disconnect()

    async def connect(self) -> None:
        """
        Connect to the MCP server.

        Raises:
            MCPConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to {self.SERVER_NAME}")

            # Load configuration
            config = await self._load_config()

            # Start server process
            self._process = await self._start_server_process()

            # Initialize session
            await self._initialize_session()

            self._connected = True
            logger.info(f"Successfully connected to {self.SERVER_NAME}")

        except Exception as e:
            logger.error(f"Failed to connect to {self.SERVER_NAME}: {e}")
            raise MCPConnectionError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """
        Disconnect from the MCP server.
        """
        if not self._connected:
            return

        try:
            logger.info(f"Disconnecting from {self.SERVER_NAME}")

            # Clean up session
            if self._session_id:
                await self._cleanup_session()

            # Terminate process
            if self._process and not self._process.returncode:
                self._process.terminate()
                await self._process.wait()

            self._connected = False
            self._tools_cache = None

            logger.info(f"Successfully disconnected from {self.SERVER_NAME}")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def health_check(self) -> bool:
        """
        Check if the client is healthy and operational.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self._connected:
                return False

            # Perform actual health check
            tools = await self.list_available_tools()
            return len(tools) > 0

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from the MCP server.

        Returns:
            List of tool definitions

        Raises:
            MCPToolError: If listing tools fails
        """
        if not self._connected:
            raise MCPConnectionError("Not connected to server")

        try:
            # Use cache if available
            if self._tools_cache is not None:
                return self._tools_cache

            # Query tools from server
            tools = await self._query_tools()

            # Cache the result
            self._tools_cache = tools

            logger.debug(f"Found {len(tools)} tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise MCPToolError(f"Tool listing failed: {e}")

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a specific tool with arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            MCPToolError: If tool execution fails
        """
        if not self._connected:
            raise MCPConnectionError("Not connected to server")

        try:
            logger.debug(f"Calling tool {tool_name} with args: {arguments}")

            # Validate tool exists
            tools = await self.list_available_tools()
            if not any(tool["name"] == tool_name for tool in tools):
                raise MCPToolError(f"Tool '{tool_name}' not found")

            # Execute tool
            result = await self._execute_tool(tool_name, arguments)

            logger.debug(f"Tool {tool_name} completed successfully")
            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise MCPToolError(f"Tool '{tool_name}' execution failed: {e}")

    # Private methods (implementation details)

    async def _query_tools(self) -> List[Dict[str, Any]]:
        """Query available tools from the server."""
        # Implementation depends on specific MCP server protocol
        # This is a placeholder
        return [
            {
                "name": "example_tool",
                "description": "Example tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                },
            }
        ]

    async def _execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific tool."""
        # Implementation depends on specific MCP server protocol
        # This is a placeholder
        return {
            "success": True,
            "result": f"Tool {tool_name} executed with args: {arguments}",
        }

    async def _initialize_session(self) -> None:
        """Initialize MCP session."""
        # Implementation depends on specific MCP server protocol
        self._session_id = "example_session_id"

    async def _cleanup_session(self) -> None:
        """Clean up MCP session."""
        # Implementation depends on specific MCP server protocol
        self._session_id = None


# Usage Example
async def example_usage():
    """
    Example usage of the MCP client.
    """
    config_path = "mcp_config.json"

    # Context manager usage (recommended)
    async with ExampleMCPClient(config_path) as client:
        # Check health
        if not await client.health_check():
            logger.error("Client is not healthy")
            return

        # List tools
        tools = await client.list_available_tools()
        logger.info(f"Available tools: {[tool['name'] for tool in tools]}")

        # Call a tool
        result = await client.call_tool("example_tool", {"input": "test"})
        logger.info(f"Tool result: {result}")


# Error Handling Example
async def error_handling_example():
    """
    Example of proper error handling.
    """
    config_path = "mcp_config.json"

    try:
        async with ExampleMCPClient(config_path) as client:
            # Operations that might fail
            await client.call_tool("nonexistent_tool", {})

    except MCPConnectionError as e:
        logger.error(f"Connection error: {e}")
        # Handle connection issues

    except MCPToolError as e:
        logger.error(f"Tool error: {e}")
        # Handle tool execution issues

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Handle unexpected errors


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())
    asyncio.run(error_handling_example())
