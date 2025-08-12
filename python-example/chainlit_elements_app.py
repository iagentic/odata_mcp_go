#!/usr/bin/env python3
"""
Chainlit Elements Web Application for OData MCP OpenAI Client

Uses Chainlit's built-in elements for better data display and rendering.
"""

import chainlit as cl
import os
import json
import asyncio
import pandas as pd
from typing import Dict, Any, Optional, List
from mcp_openai_client import MCPOpenAIClient
import re

# Global client instance
mcp_client: Optional[MCPOpenAIClient] = None

def parse_json_data(data_str: str) -> Optional[Dict]:
    """Parse JSON data from OData response"""
    try:
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', data_str, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None
    except:
        return None

def create_dataframe(data: Dict) -> Optional[pd.DataFrame]:
    """Create a pandas DataFrame from OData response"""
    try:
        if 'value' in data and isinstance(data['value'], list):
            df = pd.DataFrame(data['value'])
            return df
        return None
    except:
        return None

def format_tool_info(tools: List) -> str:
    """Format tool information for display"""
    categories = {
        'filter': [],
        'count': [],
        'get': [],
        'search': [],
        'create': [],
        'update': [],
        'delete': [],
        'other': []
    }
    
    for tool in tools:
        name = tool.name.lower()
        if 'filter' in name:
            categories['filter'].append(tool)
        elif 'count' in name:
            categories['count'].append(tool)
        elif 'get' in name:
            categories['get'].append(tool)
        elif 'search' in name:
            categories['search'].append(tool)
        elif 'create' in name:
            categories['create'].append(tool)
        elif 'update' in name:
            categories['update'].append(tool)
        elif 'delete' in name:
            categories['delete'].append(tool)
        else:
            categories['other'].append(tool)
    
    result = []
    for category, tools_list in categories.items():
        if tools_list:
            result.append(f"**{category.title()} Operations ({len(tools_list)}):**")
            for tool in tools_list[:3]:  # Show first 3 tools per category
                result.append(f"- {tool.name}")
            if len(tools_list) > 3:
                result.append(f"- ... and {len(tools_list) - 3} more")
            result.append("")
    
    return "\n".join(result)

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    global mcp_client
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        await cl.Message(
            content="❌ **OpenAI API key required!**\n\n"
                   "Please set the `OPENAI_API_KEY` environment variable or provide it in the settings."
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
    tool_count = len(mcp_client.tools)
    tool_info = format_tool_info(mcp_client.tools)
    
    init_msg.content = (
        f"✅ **Connected successfully!**\n\n"
        f"📊 **Loaded {tool_count} tools** from the OData service\n\n"
        f"{tool_info}"
        f"💬 **Try asking questions like:**\n"
        f"- \"Show me the first 5 products\"\n"
        f"- \"Find products with price less than 20\"\n"
        f"- \"Get information about categories\"\n"
        f"- \"How many products are there?\"\n"
        f"- \"Show me products from the Beverages category\"\n"
        f"- \"Create a table of products with their prices\""
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
        
        # Try to parse and visualize the data
        parsed_data = parse_json_data(result)
        
        if parsed_data:
            df = create_dataframe(parsed_data)
            
            if df is not None and not df.empty:
                # Create enhanced data display using Chainlit elements
                processing_msg.content = "📊 **Data retrieved successfully!**"
                await processing_msg.update()
                
                # Show summary using text
                summary_text = f"""
📈 **Data Summary**

• **Total Records:** {len(df)}
• **Columns:** {len(df.columns)}
• **Sample Columns:** {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}
"""
                await cl.Message(content=summary_text).send()
                
                # Show data using Chainlit's DataTable element
                if len(df) > 0:
                    # Convert DataFrame to list of dictionaries for DataTable
                    data = df.head(20).to_dict('records')
                    
                    # Create DataTable element
                    await cl.DataTable(
                        data=data,
                        name="odata_results",
                        description=f"Showing {len(data)} of {len(df)} records"
                    ).send()
                
                # If there are more records, show a note
                if len(df) > 20:
                    await cl.Message(
                        content=f"📝 **Note:** Showing first 20 of {len(df)} records. Use specific filters to see more data."
                    ).send()
                
                # Show export information
                await cl.Message(
                    content=f"📥 **Export Options:**\n"
                           f"• Use the table above - you can copy/paste or download\n"
                           f"• Use the raw JSON below for API integration\n"
                           f"• Contact your administrator for bulk export options"
                ).send()
                
                # Show raw JSON for debugging (truncated)
                debug_text = f"🔍 **Raw Response (first 500 chars):**\n```json\n{json.dumps(parsed_data, indent=2)[:500]}...\n```"
                await cl.Message(content=debug_text).send()
                
            else:
                # No structured data, show raw result
                processing_msg.content = f"📊 **Result:**\n\n```json\n{result}\n```"
                await processing_msg.update()
        else:
            # No JSON data found, show raw result
            processing_msg.content = f"📊 **Result:**\n\n```json\n{result}\n```"
            await processing_msg.update()
        
    except Exception as e:
        processing_msg.content = f"❌ **Error:** {str(e)}"
        await processing_msg.update()

# Chainlit configuration - using compatible API
# Note: set_page_config and set_settings are not available in all Chainlit versions
# The app will work without these configurations 