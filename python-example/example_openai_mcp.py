#!/usr/bin/env python3
"""
Simple example of using OpenAI with OData MCP server

This script demonstrates basic usage of the MCP OpenAI client.
"""

import os
from mcp_openai_client import MCPOpenAIClient

def main():
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Create client
    client = MCPOpenAIClient()
    
    # Initialize MCP connection
    if not client.initialize_mcp():
        print("❌ Failed to initialize MCP connection")
        print("Make sure the OData MCP server is running:")
        print("./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/")
        return
    
    # Example queries
    queries = [
        "Show me the first 3 products",
        "Get information about categories",
        "Find products with price less than 20",
        "How many products are there in total?",
        "Show me products from the Beverages category"
    ]
    
    print("🚀 OData MCP OpenAI Example")
    print("=" * 50)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        result = client.query_with_openai(query)
        print(f"📊 Result:\n{result}")
        print("=" * 50)

if __name__ == "__main__":
    main() 