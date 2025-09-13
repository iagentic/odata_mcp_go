#!/usr/bin/env python3
"""
Chainlit Markdown Web Application for OData MCP OpenAI Client

Uses markdown formatting for reliable data display with both structured content and raw JSON.
"""

import chainlit as cl
import os
import json
import asyncio
import pandas as pd
from typing import Dict, Any, Optional, List
from mcp_openai_client import MCPOpenAIClient
import re
from dotenv import load_dotenv

load_dotenv()

# Global client instance - initialized once at app startup
mcp_client: Optional[MCPOpenAIClient] = None
mcp_initialized: bool = False

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

def create_markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Create a markdown table from DataFrame"""
    if df.empty:
        return "No data available"
    
    # Get column names
    columns = list(df.columns)
    
    # Create header
    header = "| " + " | ".join(str(col) for col in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    
    # Create rows with safe value conversion
    rows = []
    for idx, row in df.head(max_rows).iterrows():
        row_values = []
        for val in row.values:
            if isinstance(val, dict):
                # Handle OData deferred objects
                if '__deferred' in val:
                    row_values.append("🔗 Deferred")
                else:
                    row_values.append("📦 Object")
            else:
                row_values.append(str(val))
        
        row_str = "| " + " | ".join(row_values) + " |"
        rows.append(row_str)
    
    # Combine all parts
    result = f"""
## 📊 Data Table ({len(df.head(max_rows))} of {len(df)} records)

{header}
{separator}
"""
    result += "\n".join(rows)
    
    return result

def create_markdown_summary(df: pd.DataFrame) -> str:
    """Create markdown summary of DataFrame"""
    result = f"""
## 📈 Data Summary

| Metric | Value |
|--------|-------|
| **Total Records** | {len(df)} |
| **Columns** | {len(df.columns)} |
| **Sample Columns** | {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''} |

### 📋 Column Details

| Column | Data Type | Sample Values |
|--------|-----------|---------------|
"""
    # Add column details
    for col in df.columns[:10]:  # Show first 10 columns
        try:
            # Handle different data types safely
            sample_values = df[col].dropna().head(3).tolist()
            
            # Convert complex objects to strings
            sample_str_parts = []
            for val in sample_values:
                if isinstance(val, dict):
                    # Handle OData deferred objects
                    if '__deferred' in val:
                        sample_str_parts.append("OData Deferred")
                    else:
                        sample_str_parts.append("Complex Object")
                else:
                    sample_str_parts.append(str(val))
            
            sample_str = ", ".join(sample_str_parts)
            if len(sample_str) > 50:
                sample_str = sample_str[:47] + "..."
            
            result += f"| {col} | {df[col].dtype} | {sample_str} |\n"
        except Exception as e:
            # Fallback for problematic columns
            result += f"| {col} | {df[col].dtype} | Error processing |\n"
    
    return result

def create_markdown_statistics(df: pd.DataFrame) -> str:
    """Create markdown statistics section"""
    stats = []
    
    # Numeric columns statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        stats.append("### 📊 Numeric Statistics")
        stats.append("")
        stats.append("| Column | Min | Max | Mean | Median |")
        stats.append("|--------|-----|-----|------|--------|")
        
        for col in numeric_cols[:5]:  # Show first 5 numeric columns
            try:
                stats.append(f"| {col} | {df[col].min():.2f} | {df[col].max():.2f} | {df[col].mean():.2f} | {df[col].median():.2f} |")
            except Exception as e:
                stats.append(f"| {col} | Error | Error | Error | Error |")
    
    # Categorical columns statistics
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        stats.append("")
        stats.append("### 📋 Categorical Statistics")
        stats.append("")
        stats.append("| Column | Unique Values | Most Common |")
        stats.append("|--------|---------------|-------------|")
        
        for col in categorical_cols[:5]:  # Show first 5 categorical columns
            try:
                # Handle complex objects safely
                unique_count = df[col].nunique()
                
                # Find most common value safely
                try:
                    mode_values = df[col].mode()
                    if len(mode_values) > 0:
                        most_common = mode_values.iloc[0]
                        if isinstance(most_common, dict):
                            if '__deferred' in most_common:
                                most_common = "OData Deferred"
                            else:
                                most_common = "Complex Object"
                        else:
                            most_common = str(most_common)
                    else:
                        most_common = "N/A"
                except Exception:
                    most_common = "Error"
                
                stats.append(f"| {col} | {unique_count} | {most_common} |")
            except Exception as e:
                stats.append(f"| {col} | Error | Error |")
    
    return "\n".join(stats)

def format_tool_info(tools: List) -> str:
    """Format tool information for display - optimized for large tool sets"""
    # For large tool sets, just show counts without processing all tools
    if len(tools) > 100:
        return f"🔧 **Large tool set detected ({len(tools)} tools)**\n\n" \
               f"All OData operations are available. Use natural language to query the service."
    
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
    
    # Process only first 50 tools to avoid performance issues
    sample_tools = tools[:50]
    
    for tool in sample_tools:
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
    
    # Add note if we sampled tools
    if len(tools) > 50:
        result.append(f"📝 **Note:** Showing sample of first 50 tools. All {len(tools)} tools are available for use.")
    
    return "\n".join(result)

def initialize_mcp_once():
    """Initialize MCP client once at app startup"""
    global mcp_client, mcp_initialized
    
    if mcp_initialized:
        return True
    
    try:
        # Check for OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OpenAI API key required! Set OPENAI_API_KEY environment variable.")
            return False
        
        # Create MCP client
        mcp_client = MCPOpenAIClient()
        
        # Initialize MCP connection
        print("🔄 Initializing MCP connection...")
        if mcp_client.initialize_mcp():
            print(f"✅ MCP initialized successfully with {len(mcp_client.tools)} tools")
            mcp_initialized = True
            return True
        else:
            print("❌ Failed to initialize MCP connection")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing MCP: {e}")
        return False

# Initialize MCP at module import time (app startup)
print("🚀 Starting Chainlit app...")
if not initialize_mcp_once():
    print("⚠️  MCP initialization failed. App will show error messages to users.")

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    global mcp_client, mcp_initialized
    
    # Check if MCP was initialized at app startup
    if not mcp_initialized or not mcp_client:
        await cl.Message(
            content="❌ **MCP server not available!**\n\n"
                   "The OData MCP server connection failed during app startup.\n"
                   "Please check the server logs and ensure the MCP server is running:\n"
                   "```bash\n"
                   "./odata-mcp --transport http --insecure https://your-odata-service/\n"
                   "```"
        ).send()
        return
    
    # Show tool count and status without sending all tool details
    tool_count = len(mcp_client.tools)
    
    # Only show sample tools if count is reasonable, otherwise just show status
    if tool_count <= 50:
        # Small tool set - show sample tools
        tool_info = format_tool_info(mcp_client.tools)
        tool_display = f"📊 **Loaded {tool_count} tools** from the OData service\n\n{tool_info}"
    else:
        # Large tool set - just show count and status
        tool_display = f"📊 **Loaded {tool_count} tools** from the OData service\n\n"
        tool_display += f"🔧 **Tool Categories Available:**\n"
        tool_display += f"• **Filter/List Operations** - Query and filter data\n"
        tool_display += f"• **Get Operations** - Retrieve specific records\n"
        tool_display += f"• **Search Operations** - Full-text search\n"
        tool_display += f"• **Count Operations** - Get record counts\n"
        tool_display += f"• **Create/Update/Delete** - Modify data (if enabled)\n\n"
    
    # Create and send the welcome message
    welcome_msg = cl.Message(
        content=f"✅ **Connected successfully!**\n\n"
                f"{tool_display}"
                f"💬 **Try asking questions like:**\n"
                f"- \"Show me the first 5 contacts\"\n"
                f"- \"Find accounts with revenue greater than 100000\"\n"
                f"- \"Get information about leads\"\n"
                f"- \"How many contacts are there?\"\n"
                f"- \"Show me contacts from the Sales team\"\n"
                f"- \"Create a table of accounts with their details\"\n"
                f"- \"Search for contacts with email containing 'gmail'\""
    )
    await welcome_msg.send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    global mcp_client, mcp_initialized
    
    if not mcp_initialized or not mcp_client:
        await cl.Message(
            content="❌ **MCP server not available!** Please check server status."
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
            print("parsed_data: ", parsed_data)
            df = create_dataframe(parsed_data)
            
            if df is not None and not df.empty:
                print("df: ", df)
                # Create enhanced data display using markdown
                processing_msg.content = "📊 **Data retrieved successfully!**"
                await processing_msg.update()
                
                try:
                    # Show summary using markdown
                    summary_md = create_markdown_summary(df)
                    await cl.Message(content=summary_md).send()
                    
                    # Show statistics using markdown
                    stats_md = create_markdown_statistics(df)
                    if stats_md.strip():
                        await cl.Message(content=stats_md).send()
                    
                    # Show data table using markdown
                    table_md = create_markdown_table(df)
                    await cl.Message(content=table_md).send()
                    
                    # If there are more records, show a note
                    if len(df) > 20:
                        await cl.Message(
                            content=f"📝 **Note:** Showing first 20 of {len(df)} records. Use specific filters to see more data."
                        ).send()
                    
                    # Show export information
                    await cl.Message(
                        content=f"📥 **Export Options:**\n"
                               f"• Copy the markdown table above and paste into any markdown editor\n"
                               f"• Use the raw JSON below for API integration\n"
                               f"• Convert markdown to CSV using online tools"
                    ).send()
                    
                    # Show raw JSON for debugging (full response)
                    debug_text = f"🔍 **Raw JSON Response:**\n```json\n{json.dumps(parsed_data, indent=2)}\n```"
                    await cl.Message(content=debug_text).send()
                    
                except Exception as e:
                    # Fallback for processing errors
                    await cl.Message(
                        content=f"⚠️ **Processing Warning:** Some data could not be displayed properly due to complex object types.\n\n"
                               f"**Error:** {str(e)}\n\n"
                               f"**Raw Data Available:** The raw JSON below contains the complete data."
                    ).send()
                    
                    # Show raw JSON as fallback
                    debug_text = f"🔍 **Raw JSON Response:**\n```json\n{json.dumps(parsed_data, indent=2)}\n```"
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