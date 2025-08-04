# HTTP Transport Testing Guide

This guide covers all methods to test the HTTP/SSE transport functionality of the OData MCP Bridge.

## Prerequisites

1. **Build the binary** (if not already built):
   ```bash
   make build
   # or
   go build -o odata-mcp cmd/odata-mcp/main.go
   ```

2. **Install required tools**:
   - `curl` - for HTTP requests
   - `jq` - for JSON parsing (optional but recommended)
   - A web browser - for testing the HTML client

## Quick Start

### 1. Start the HTTP Server

```bash
# Basic HTTP server on localhost:8080
./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/

# Custom port
./odata-mcp --transport http --http-addr localhost:3000 https://services.odata.org/V2/Northwind/Northwind.svc/

# With verbose output for debugging
./odata-mcp --transport http --verbose https://services.odata.org/V2/Northwind/Northwind.svc/
```

### 2. Test with curl (Quick Test)

```bash
# Run the simple curl test script
./test_http_curl.sh
```

This will test:
- Health endpoint
- SSE connection
- RPC initialize
- Tools list
- Tool call
- Error handling

### 3. Test with Web Browser

1. Start the server (see step 1)
2. Open `test_http_sse.html` in your web browser
3. Click "Connect SSE" to establish connection
4. Use the buttons to test different functionality

### 4. Comprehensive Testing

```bash
# Run all tests
./test_http_transport.sh

# Test specific components
./test_http_transport.sh --health
./test_http_transport.sh --rpc
./test_http_transport.sh --sse
./test_http_transport.sh --errors
./test_http_transport.sh --security
```

## Available Endpoints

When the HTTP server is running, these endpoints are available:

### Health Check
```bash
curl http://localhost:8080/health
```
**Response**: `{"status":"ok"}`

### Server-Sent Events (SSE)
```bash
curl -N -H 'Accept: text/event-stream' http://localhost:8080/sse
```
**Purpose**: Real-time bidirectional communication

### JSON-RPC Endpoint
```bash
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```
**Purpose**: Request/response communication

## Manual Testing with curl

### 1. Test Health Endpoint
```bash
curl http://localhost:8080/health
```

### 2. Test SSE Connection
```bash
# Connect to SSE (will show events)
curl -N -H 'Accept: text/event-stream' http://localhost:8080/sse
```

### 3. Test RPC Initialize
```bash
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "0.1.0",
      "capabilities": {},
      "clientInfo": {
        "name": "Test Client",
        "version": "1.0.0"
      }
    }
  }'
```

### 4. Test Tools List
```bash
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### 5. Test Tool Call
```bash
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "filter_Products_for_northwind",
      "arguments": {
        "$top": 3
      }
    }
  }'
```

### 6. Test Error Handling
```bash
# Invalid JSON
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d 'invalid json'

# Non-existent tool
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "non_existent_tool",
      "arguments": {}
    }
  }'
```

## Web Client Testing

The `test_http_sse.html` file provides a comprehensive web-based test client with:

- **Connection Management**: Connect/disconnect to SSE
- **Health Check**: Test the health endpoint
- **RPC Testing**: Initialize, list tools, call tools
- **Interactive Tool Testing**: Enter tool names and parameters
- **Real-time Messages**: View all communication in real-time

### Features:
- Visual status indicators
- Timestamped messages
- Color-coded message types (request, response, error, success)
- Interactive tool parameter input
- Connection state management

## Security Testing

### Test Localhost Restriction
```bash
# This should fail (security feature)
./odata-mcp --transport http --http-addr 0.0.0.0:8080 https://services.odata.org/V2/Northwind/Northwind.svc/

# This should work (with expert flag)
./odata-mcp --transport http --http-addr 0.0.0.0:8080 --i-am-security-expert-i-know-what-i-am-doing https://services.odata.org/V2/Northwind/Northwind.svc/
```

### Test Different Ports
```bash
# Test custom port
./odata-mcp --transport http --http-addr localhost:3000 https://services.odata.org/V2/Northwind/Northwind.svc/
curl http://localhost:3000/health
```

## Troubleshooting

### Common Issues

1. **Server won't start**:
   ```bash
   # Check if port is in use
   lsof -i :8080
   
   # Kill existing process
   pkill -f "odata-mcp"
   ```

2. **Connection refused**:
   - Ensure server is running
   - Check firewall settings
   - Verify port number

3. **SSE connection fails**:
   - Check browser console for errors
   - Verify Accept header is set correctly
   - Check CORS settings if testing from different domain

4. **RPC calls fail**:
   - Verify Content-Type header is set to `application/json`
   - Check JSON format is valid
   - Ensure tool name exists

### Debug Mode

Start server with verbose output:
```bash
./odata-mcp --transport http --verbose --trace-mcp https://services.odata.org/V2/Northwind/Northwind.svc/
```

### Log Analysis

Check server logs for errors:
```bash
# If using background server
tail -f server.log

# Check for specific errors
grep -i error server.log
```

## Performance Testing

### Load Testing with curl
```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -s -X POST http://localhost:8080/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":'$i',"method":"tools/list","params":{}}' &
done
wait
```

### SSE Connection Testing
```bash
# Test multiple SSE connections
for i in {1..5}; do
  curl -N -H 'Accept: text/event-stream' http://localhost:8080/sse > sse_$i.log &
done
```

## Integration Testing

### Test with Real OData Services

```bash
# Test with different OData services
./odata-mcp --transport http https://services.odata.org/V4/Northwind/Northwind.svc/

# Test with authentication
./odata-mcp --transport http --user username --password password https://my-service.com/odata/

# Test with read-only mode
./odata-mcp --transport http --read-only https://services.odata.org/V2/Northwind/Northwind.svc/
```

### Test Different Configurations

```bash
# Test with tool shrinking
./odata-mcp --transport http --tool-shrink https://services.odata.org/V2/Northwind/Northwind.svc/

# Test with entity filtering
./odata-mcp --transport http --entities "Products,Categories" https://services.odata.org/V2/Northwind/Northwind.svc/

# Test with operation filtering
./odata-mcp --transport http --disable "cud" https://services.odata.org/V2/Northwind/Northwind.svc/
```

## Expected Results

### Successful Health Check
```json
{"status":"ok"}
```

### Successful Initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "0.1.0",
    "capabilities": {},
    "serverInfo": {
      "name": "odata-mcp",
      "version": "0.1.0"
    }
  }
}
```

### Successful Tools List
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "filter_Products_for_northwind",
        "description": "Filter Products entities",
        "inputSchema": {
          "type": "object",
          "properties": {
            "$top": {"type": "integer"},
            "$skip": {"type": "integer"},
            "$filter": {"type": "string"}
          }
        }
      }
    ]
  }
}
```

### Successful Tool Call
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Retrieved 3 Products from Northwind service..."
      }
    ]
  }
}
```

## Security Considerations

⚠️ **IMPORTANT**: The HTTP transport has NO AUTHENTICATION by default!

- **Default**: Only accessible from localhost
- **Expert mode**: Can bind to 0.0.0.0 with `--i-am-security-expert-i-know-what-i-am-doing`
- **Production use**: Should be behind a reverse proxy with authentication
- **Never expose to internet**: Without additional security measures

## Next Steps

After testing HTTP transport:

1. **Test STDIO transport**: `./odata-mcp https://services.odata.org/V2/Northwind/Northwind.svc/`
2. **Test with Claude Desktop**: Configure in Claude Desktop settings
3. **Test with other MCP clients**: RooCode, GitHub Copilot, etc.
4. **Test with real OData services**: Your enterprise OData endpoints

For more information, see:
- [README.md](README.md) - Main documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide
- [SECURITY.md](SECURITY.md) - Security considerations 