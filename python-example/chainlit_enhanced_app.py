#!/usr/bin/env python3
"""
Enhanced Chainlit Web Application for OData MCP OpenAI Client

Advanced version with improved structured output, data visualization, and user experience.
"""

import chainlit as cl
import os
import json
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from mcp_openai_client import MCPOpenAIClient
import re
import base64
from io import StringIO

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

def create_styled_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Create a styled HTML table with better formatting"""
    # Limit rows for display
    df_display = df.head(max_rows)
    
    # Create styled HTML table
    styled_html = f"""
    <style>
    .data-table {{
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }}
    .data-table th {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.5px;
    }}
    .data-table td {{
        padding: 10px 8px;
        border-bottom: 1px solid #f0f0f0;
        background-color: white;
    }}
    .data-table tr:nth-child(even) td {{
        background-color: #f8f9fa;
    }}
    .data-table tr:hover td {{
        background-color: #e3f2fd;
        transition: background-color 0.2s ease;
    }}
    .table-container {{
        margin: 20px 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .table-header {{
        background: #f8f9fa;
        padding: 15px;
        border-bottom: 1px solid #dee2e6;
        font-weight: 600;
        color: #495057;
    }}
    </style>
    <div class="table-container">
        <div class="table-header">
            📊 Data Table ({len(df_display)} of {len(df)} records)
        </div>
        {df_display.to_html(index=False, classes='data-table', escape=False)}
    </div>
    """
    return styled_html

def create_charts(df: pd.DataFrame) -> List[str]:
    """Create various charts based on data types"""
    charts = []
    
    try:
        # Numeric columns for charts
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Bar chart for categorical data
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Group by categorical column and sum numeric column
            chart_data = df.groupby(cat_col)[num_col].sum().reset_index()
            
            fig = px.bar(
                chart_data, 
                x=cat_col, 
                y=num_col,
                title=f'{num_col} by {cat_col}',
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            charts.append(fig.to_html(full_html=False))
        
        # Histogram for numeric data
        if len(numeric_cols) > 0:
            num_col = numeric_cols[0]
            fig = px.histogram(
                df, 
                x=num_col,
                title=f'Distribution of {num_col}',
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            charts.append(fig.to_html(full_html=False))
            
    except Exception as e:
        print(f"Chart creation error: {e}")
    
    return charts

def create_export_links(df: pd.DataFrame) -> str:
    """Create download links for data export"""
    try:
        # CSV export
        csv_data = df.to_csv(index=False)
        csv_b64 = base64.b64encode(csv_data.encode()).decode()
        
        # JSON export
        json_data = df.to_json(orient='records', indent=2)
        json_b64 = base64.b64encode(json_data.encode()).decode()
        
        export_html = f"""
        <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">
            <h4 style="margin: 0 0 10px 0; color: #495057;">📥 Export Data</h4>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="data:text/csv;charset=utf-8;base64,{csv_b64}" 
                   download="data.csv" 
                   style="padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; font-size: 14px;">
                    📄 Download CSV
                </a>
                <a href="data:application/json;charset=utf-8;base64,{json_b64}" 
                   download="data.json" 
                   style="padding: 8px 16px; background: #17a2b8; color: white; text-decoration: none; border-radius: 4px; font-size: 14px;">
                    📄 Download JSON
                </a>
            </div>
        </div>
        """
        return export_html
    except Exception as e:
        return f"<p>Export error: {e}</p>"

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
        f"- \"Create a table of products with their prices\"\n"
        f"- \"Show me a chart of product prices by category\""
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
                # Create enhanced data display
                processing_msg.content = "📊 **Data retrieved successfully!**"
                await processing_msg.update()
                
                # Show summary with enhanced styling
                summary_html = f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <h3 style="margin: 0 0 15px 0;">📈 Data Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold;">{len(df)}</div>
                            <div style="font-size: 14px;">Total Records</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold;">{len(df.columns)}</div>
                            <div style="font-size: 14px;">Columns</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: bold;">{', '.join(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}</div>
                            <div style="font-size: 14px;">Sample Columns</div>
                        </div>
                    </div>
                </div>
                """
                await cl.Message(content=summary_html).send()
                
                # Show styled data table
                table_html = create_styled_table(df)
                await cl.Message(content=table_html).send()
                
                # Create and show charts
                charts = create_charts(df)
                for chart_html in charts:
                    await cl.Message(content=chart_html).send()
                
                # Show export options
                export_html = create_export_links(df)
                await cl.Message(content=export_html).send()
                
                # If there are more records, show a note
                if len(df) > 20:
                    await cl.Message(
                        content=f"📝 **Note:** Showing first 20 of {len(df)} records. Use specific filters to see more data."
                    ).send()
                
                # Show raw JSON for debugging (collapsed)
                debug_html = f"""
                <details style="margin: 15px 0;">
                    <summary style="cursor: pointer; padding: 10px; background: #f8f9fa; border-radius: 5px; font-weight: bold;">
                        🔍 Debug Information (Click to expand)
                    </summary>
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px;">
{json.dumps(parsed_data, indent=2)[:1000]}...
                    </pre>
                </details>
                """
                await cl.Message(content=debug_html).send()
                
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