#!/usr/bin/env python3
"""
Chainlit Web Application for OData MCP OpenAI Client

This provides a web interface for querying OData services using natural language.
"""

import chainlit as cl
import os
import json
import asyncio
from typing import Dict, Any, Optional
from mcp_openai_client import MCPOpenAIClient

# Global client instance
mcp_client: Optional[MCPOpenAIClient] = None

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    global mcp_client
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        await cl.Message(
            content="❌ **OpenAI API key required!**\n\nPlease set the `OPENAI_API_KEY` environment variable or provide it in the settings."
        ).send()
        return
    
    # Create MCP client
    mcp_client = MCPOpenAIClient()
    
    # Initialize MCP connection
    init_msg = cl.Message(content="🔄 **Initializing connection to OData MCP server...**")
    await init_msg.send()
    
    if not mcp_client.initialize_mcp():
        init_msg.content = (
            "❌ **Failed to connect to MCP server!**\n\n"
            "Please ensure the OData MCP server is running:\n"
            "```bash\n"
            "./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/\n"
            "```"
        )
        await init_msg.update()
        return
    
    # Show available tools
    tool_descriptions = mcp_client.get_tool_descriptions()
    tool_count = len(mcp_client.tools)
    
    init_msg.content = (
        f"✅ **Connected successfully!**\n\n"
        f"📊 **Loaded {tool_count} tools** from the OData service\n\n"
        f"💡 **Available operations:**\n"
        f"- Query products, categories, suppliers, and more\n"
        f"- Filter data with natural language\n"
        f"- Get counts and statistics\n"
        f"- Search and sort data\n\n"
        f"💬 **Try asking questions like:**\n"
        f"- \"Show me the first 5 products\"\n"
        f"- \"Find products with price less than 20\"\n"
        f"- \"Get information about categories\"\n"
        f"- \"How many products are there?\"\n"
        f"- \"Show me products from the Beverages category\""
    )
    await init_msg.update()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    global mcp_client
    
    if not mcp_client or not mcp_client.initialized:
        await cl.Message(
            content="❌ **Client not initialized!** Please restart the chat."
        ).send()
        return
    
    # Show processing message
    processing_msg = cl.Message(content="🔄 **Processing your query...**")
    await processing_msg.send()
    
    try:
        # Process query with OpenAI
        result = mcp_client.query_with_openai(message.content)
        
        # Update processing message with result
        processing_msg.content = f"📊 **Result:**\n\n```json\n{result}\n```"
        await processing_msg.update()
        
    except Exception as e:
        processing_msg.content = f"❌ **Error:** {str(e)}"
        await processing_msg.update()

# Settings update handler removed for compatibility
# Use environment variables for configuration instead

# Chainlit configuration - using compatible API
# Note: set_page_config and set_settings are not available in all Chainlit versions
# The app will work without these configurations 