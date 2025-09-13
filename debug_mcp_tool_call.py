#!/usr/bin/env python3
"""
Debug script to test MCP tool calls and capture raw responses
"""

import requests
import json
import time

def debug_tool_call(mcp_url="http://localhost:8080", tool_name="filter_OpportunityCollection_for_v1", arguments=None):
    """Debug a specific tool call"""
    if arguments is None:
        arguments = {"$filter": "CloseDate ge 2024-06-01 and CloseDate le 2024-06-30"}
    
    print(f"🔍 DEBUG: Testing tool call to {mcp_url}")
    print(f"🔍 DEBUG: Tool: {tool_name}")
    print(f"🔍 DEBUG: Arguments: {arguments}")
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{mcp_url}/health")
        print(f"🔍 DEBUG: Health check status: {health_response.status_code}")
        print(f"🔍 DEBUG: Health response: {health_response.text}")
    except Exception as e:
        print(f"❌ DEBUG: Health check failed: {e}")
        return
    
    # Make the tool call
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        print(f"🔍 DEBUG: Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{mcp_url}/rpc",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"🔍 DEBUG: HTTP status: {response.status_code}")
        print(f"🔍 DEBUG: HTTP headers: {dict(response.headers)}")
        print(f"🔍 DEBUG: Raw response text: {repr(response.text)}")
        print(f"🔍 DEBUG: Response text length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"🔍 DEBUG: Parsed JSON: {json.dumps(result, indent=2)}")
                
                if "error" in result:
                    print(f"❌ DEBUG: MCP error: {result['error']}")
                elif "result" in result:
                    print(f"✅ DEBUG: MCP success")
                    if "content" in result["result"]:
                        content = result["result"]["content"]
                        print(f"🔍 DEBUG: Content: {content}")
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: JSON decode error: {e}")
                print(f"❌ DEBUG: Error at position: {e.pos}")
                print(f"❌ DEBUG: Error line: {e.lineno}, column: {e.colno}")
        else:
            print(f"❌ DEBUG: HTTP error: {response.status_code}")
            print(f"❌ DEBUG: Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ DEBUG: Request failed: {e}")
        print(f"❌ DEBUG: Exception type: {type(e)}")

if __name__ == "__main__":
    # Test the specific tool that's failing
    debug_tool_call()
