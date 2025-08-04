#!/bin/bash

# Simple HTTP Transport Test with curl
# This script provides quick tests for HTTP transport functionality

SERVER_URL="http://localhost:8080"

echo "=== OData MCP HTTP Transport Test ==="
echo "Server URL: $SERVER_URL"
echo ""

# Check if server is running
echo "1. Testing health endpoint..."
if curl -s "$SERVER_URL/health" > /dev/null; then
    echo "✅ Health endpoint is working"
    curl -s "$SERVER_URL/health" | jq '.' 2>/dev/null || curl -s "$SERVER_URL/health"
else
    echo "❌ Health endpoint failed - make sure server is running"
    echo "Start server with: ./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/"
    exit 1
fi

echo ""
echo "2. Testing SSE connection..."
echo "Connecting to SSE endpoint (will timeout after 5 seconds)..."
timeout 5s curl -N -H 'Accept: text/event-stream' "$SERVER_URL/sse" || echo "SSE connection test completed"

echo ""
echo "3. Testing RPC initialize..."
response=$(curl -s -X POST "$SERVER_URL/rpc" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "curl-test",
                "version": "1.0.0"
            }
        }
    }')

if echo "$response" | grep -q '"result"'; then
    echo "✅ Initialize successful"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
else
    echo "❌ Initialize failed: $response"
fi

echo ""
echo "4. Testing tools/list..."
response=$(curl -s -X POST "$SERVER_URL/rpc" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }')

if echo "$response" | grep -q '"result"'; then
    echo "✅ Tools list successful"
    tool_count=$(echo "$response" | jq '.result.tools | length' 2>/dev/null || echo "unknown")
    echo "Found $tool_count tools"
else
    echo "❌ Tools list failed: $response"
fi

echo ""
echo "5. Testing tool call..."
response=$(curl -s -X POST "$SERVER_URL/rpc" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "filter_Alphabetical_list_of_products_for_NorthSvc",
            "arguments": {
                "$top": 2
            }
        }
    }')

if echo "$response" | grep -q '"result"'; then
    echo "✅ Tool call successful"
    echo "$response" | jq '.result.content[0].text' 2>/dev/null || echo "$response"
else
    echo "❌ Tool call failed: $response"
fi

echo ""
echo "6. Testing error handling..."
response=$(curl -s -X POST "$SERVER_URL/rpc" \
    -H "Content-Type: application/json" \
    -d 'invalid json')

if echo "$response" | grep -q '"error"'; then
    echo "✅ Invalid JSON handled correctly"
else
    echo "❌ Invalid JSON not handled properly: $response"
fi

echo ""
echo "=== HTTP Transport Test Complete ==="
echo ""
echo "To test with the web client, open test_http_sse.html in your browser"
echo "To test with the comprehensive script, run: ./test_http_transport.sh" 