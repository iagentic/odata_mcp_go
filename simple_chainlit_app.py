#!/usr/bin/env python3
"""
Simple SAP C4C PoC Chainlit Application

Uses OpenAI Agents SDK with proper handoffs for LLM-driven routing.
"""

import os
import sys
import logging
import chainlit as cl
from openai import OpenAI

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poc_c4c.config import settings
from poc_c4c.mcp.clients import MCPClient
from poc_c4c.agents import process_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global components
_openai_client: OpenAI | None = None
_mcp_client: MCPClient | None = None

def _init_clients():
    """Initialize OpenAI and MCP clients"""
    global _openai_client, _mcp_client
    
    if _openai_client is not None:
        return  # Already initialized
    
    try:
        logger.info("🚀 Initializing Simple SAP C4C PoC Application...")
        
        # Initialize OpenAI client
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        _openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Initialize MCP client
        _mcp_client = MCPClient(base_url=settings.mcp_bridge_url)
        
        logger.info("✅ Simple PoC initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    try:
        # Ensure clients are initialized
        _init_clients()
        
        welcome_message = """# 🌟 Simple SAP C4C Assistant

I'm your intelligent assistant for SAP Cloud for Customer data. I use **LLM-driven routing** to automatically send your queries to the right specialized agents.

## 🧠 **How I Work**
- **Smart Routing**: I analyze your query and route it to the appropriate agent
- **Sales Agent**: Handles opportunities, deals, and sales data
- **Service Agent**: Handles service requests, tickets, and support issues

## 🚀 **Try These Examples**
- "Show me recent opportunities"
- "Find high priority service requests"
- "What deals are closing this month?"
- "Show me open support tickets"

Ask me anything in natural language!"""

        await cl.Message(
            content=welcome_message,
            author="Assistant"
        ).send()
        
    except Exception as e:
        logger.error(f"Chat start error: {e}")
        await cl.Message(
            content=f"❌ **Startup Error**\n\n{str(e)}\n\nPlease check the server configuration.",
            author="System"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages with LLM-driven routing"""
    try:
        # Process query using the multi-agent system
        result = await process_query(message.content, _openai_client, _mcp_client)
        
        # Display the result
        await cl.Message(
            content=result.final_output,
            author="Assistant"
        ).send()
        
    except Exception as e:
        logger.error(f"Query handling error: {e}")
        await cl.Message(
            content=f"❌ **Error**\n\n{str(e)}\n\nPlease try again.",
            author="System"
        ).send()

if __name__ == "__main__":
    # Initialize the application when run directly
    try:
        _init_clients()
        print("✅ Simple SAP C4C PoC initialized successfully!")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)


