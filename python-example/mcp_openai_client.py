#!/usr/bin/env python3
"""
OData MCP OpenAI Client

This script demonstrates how to use OpenAI with the OData MCP server
to query and analyze OData services through natural language.

Requirements:
- openai
- requests
- json
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from openai import OpenAI
import os

@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPOpenAIClient:
    """Client for interacting with OData MCP server using OpenAI"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:8080", 
                 openai_api_key: Optional[str] = None):
        """
        Initialize the MCP OpenAI client
        
        Args:
            mcp_server_url: URL of the MCP server
            openai_api_key: OpenAI API key (will use env var OPENAI_API_KEY if not provided)
        """
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.openai_client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        self.tools: List[MCPTool] = []
        self.initialized = False
        
    def initialize_mcp(self) -> bool:
        """Initialize connection to MCP server"""
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.mcp_server_url}/health")
            if health_response.status_code != 200:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
            print("✅ Health check passed")
            
            # Initialize MCP connection
            init_response = requests.post(
                f"{self.mcp_server_url}/rpc",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "mcp-openai-client",
                            "version": "1.0.0"
                        }
                    }
                }
            )
            
            if init_response.status_code != 200:
                print(f"❌ MCP initialization failed: {init_response.status_code}")
                return False
                
            init_result = init_response.json()
            if "error" in init_result:
                print(f"❌ MCP initialization error: {init_result['error']}")
                return False
                
            print("✅ MCP initialization successful")
            
            # Get available tools
            tools_response = requests.post(
                f"{self.mcp_server_url}/rpc",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            )
            
            if tools_response.status_code != 200:
                print(f"❌ Tools list failed: {tools_response.status_code}")
                return False
                
            tools_result = tools_response.json()
            if "error" in tools_result:
                print(f"❌ Tools list error: {tools_result['error']}")
                return False
                
            # Parse tools
            for tool_data in tools_result["result"]["tools"]:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["inputSchema"]
                )
                self.tools.append(tool)
                
            print(f"✅ Loaded {len(self.tools)} tools")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a specific MCP tool"""
        if not self.initialized:
            print("❌ MCP not initialized")
            return None
            
        try:
            response = requests.post(
                f"{self.mcp_server_url}/rpc",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000),
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Tool call failed: {response.status_code}")
                return None
                
            result = response.json()
            if "error" in result:
                print(f"❌ Tool call error: {result['error']}")
                return None
                
            # Extract text content from result
            content = result["result"]["content"]
            if content and len(content) > 0:
                return content[0]["text"]
            return None
            
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return None
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all available tools"""
        descriptions = []
        for tool in self.tools:
            desc = f"- {tool.name}: {tool.description}"
            if tool.input_schema.get("properties"):
                props = list(tool.input_schema["properties"].keys())
                desc += f" (parameters: {', '.join(props)})"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def query_with_openai(self, user_query: str, model: str = "gpt-4.1-mini") -> str:
        """Use OpenAI to process a natural language query and execute appropriate MCP tools"""
        
        # Create system prompt with available tools
        system_prompt = f"""You are an AI assistant that can query OData services through MCP tools.

Available MCP tools:
{self.get_tool_descriptions()}

Your task is to:
1. Understand the user's query
2. Determine which MCP tool(s) to use
3. Provide the exact tool name and parameters in JSON format
4. Explain what you're doing

Format your response as JSON with these fields:
- "explanation": Brief explanation of what you're doing
- "tool_name": The exact MCP tool name to call
- "arguments": Dictionary of arguments for the tool
- "reasoning": Why you chose this tool and these parameters

Example response:
{{
    "explanation": "I'm querying the Products entity to get a list of products",
    "tool_name": "filter_Alphabetical_list_of_products_for_NorthSvc",
    "arguments": {{"$top": 5}},
    "reasoning": "The user wants to see products, so I'll use the filter tool with a limit of 5 items"
}}

User query: {user_query}"""

        try:
            # Get OpenAI response
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1
            )
            
            # Parse OpenAI response
            content = response.choices[0].message.content
            try:
                # Try to parse as JSON
                parsed = json.loads(content)
                return self._execute_tool_plan(parsed)
            except json.JSONDecodeError:
                # If not JSON, try to extract tool information from text
                return self._extract_and_execute_from_text(content, user_query)
                
        except Exception as e:
            return f"❌ OpenAI API error: {e}"
    
    def _execute_tool_plan(self, plan: Dict[str, Any]) -> str:
        """Execute a tool plan from OpenAI"""
        try:
            explanation = plan.get("explanation", "No explanation provided")
            tool_name = plan.get("tool_name")
            arguments = plan.get("arguments", {})
            reasoning = plan.get("reasoning", "No reasoning provided")
            
            print(f"🤖 AI Explanation: {explanation}")
            print(f"🔧 Tool: {tool_name}")
            print(f"📝 Arguments: {arguments}")
            print(f"💭 Reasoning: {reasoning}")
            print()
            
            if not tool_name:
                return "❌ No tool name provided in plan"
            
            # Call the tool
            result = self.call_tool(tool_name, arguments)
            if result:
                return f"✅ Tool executed successfully:\n\n{result}"
            else:
                return "❌ Tool execution failed"
                
        except Exception as e:
            return f"❌ Error executing tool plan: {e}"
    
    def _extract_and_execute_from_text(self, text: str, original_query: str) -> str:
        """Extract tool information from text response and execute"""
        print(f"🤖 AI Response: {text}")
        print()
        
        # Try to find tool names in the text
        for tool in self.tools:
            if tool.name.lower() in text.lower():
                print(f"🔍 Found tool reference: {tool.name}")
                # Use default arguments
                result = self.call_tool(tool.name, {"$top": 5})
                if result:
                    return f"✅ Executed {tool.name}:\n\n{result}"
        
        return f"❌ Could not determine which tool to use for: {original_query}"
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("🚀 OData MCP OpenAI Client")
        print("=" * 50)
        
        if not self.initialize_mcp():
            print("❌ Failed to initialize MCP connection")
            return
        
        print("\n💡 Available tools:")
        print(self.get_tool_descriptions())
        print("\n" + "=" * 50)
        print("💬 Ask questions about the OData service (type 'quit' to exit)")
        print("Examples:")
        print("- 'Show me the first 5 products'")
        print("- 'Get information about categories'")
        print("- 'Find products with price less than 20'")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n🤔 Your query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print("\n🔄 Processing...")
                result = self.query_with_openai(query)
                print(f"\n📊 Result:\n{result}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OData MCP OpenAI Client")
    parser.add_argument("--mcp-url", default="http://localhost:8080", 
                       help="MCP server URL")
    parser.add_argument("--openai-key", help="OpenAI API key")
    parser.add_argument("--query", help="Single query to execute")
    parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model to use")
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not args.openai_key and not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required!")
        print("Set OPENAI_API_KEY environment variable or use --openai-key")
        return
    
    client = MCPOpenAIClient(
        mcp_server_url=args.mcp_url,
        openai_api_key=args.openai_key
    )
    
    if args.query:
        # Single query mode
        if not client.initialize_mcp():
            print("❌ Failed to initialize MCP connection")
            return
        
        print(f"🤖 Processing query: {args.query}")
        result = client.query_with_openai(args.query, args.model)
        print(f"\n📊 Result:\n{result}")
    else:
        # Interactive mode
        client.interactive_mode()

if __name__ == "__main__":
    main() 