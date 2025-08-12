#!/bin/bash

# OData MCP HTTP Transport Test Script
# This script tests the HTTP/SSE transport functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="http://localhost:8080"
ODATA_SERVICE="https://services.odata.org/V2/Northwind/Northwind.svc/"
BINARY="./odata-mcp"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}Error: Binary $BINARY not found. Please build the project first.${NC}"
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if server is running
check_server() {
    if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start server in background
start_server() {
    print_status "Starting OData MCP server with HTTP transport..."
    
    # Kill any existing server
    pkill -f "odata-mcp.*--transport http" || true
    
    # Start server in background
    $BINARY --transport http --http-addr localhost:8080 "$ODATA_SERVICE" > server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    print_status "Waiting for server to start..."
    for i in {1..30}; do
        if check_server; then
            print_success "Server started successfully (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Server failed to start within 30 seconds"
    return 1
}

# Function to stop server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        print_status "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        print_success "Server stopped"
    fi
}

# Function to test health endpoint
test_health() {
    print_status "Testing health endpoint..."
    
    response=$(curl -s "$SERVER_URL/health")
    if [ $? -eq 0 ]; then
        print_success "Health endpoint working: $response"
    else
        print_error "Health endpoint failed"
        return 1
    fi
}

# Function to test SSE connection
test_sse() {
    print_status "Testing SSE connection..."
    
    # Start SSE connection in background
    curl -N -H 'Accept: text/event-stream' "$SERVER_URL/sse" > sse_output.log 2>&1 &
    SSE_PID=$!
    
    # Wait a moment for connection
    sleep 2
    
    # Check if we received any data
    if [ -s sse_output.log ]; then
        print_success "SSE connection established"
        kill $SSE_PID 2>/dev/null || true
    else
        print_error "SSE connection failed"
        kill $SSE_PID 2>/dev/null || true
        return 1
    fi
}

# Function to test RPC endpoint
test_rpc() {
    print_status "Testing RPC endpoint..."
    
    # Test initialize
    print_status "Testing initialize..."
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
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            }
        }')
    
    if echo "$response" | grep -q '"result"'; then
        print_success "Initialize successful"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        print_error "Initialize failed: $response"
        return 1
    fi
    
    # Test tools/list
    print_status "Testing tools/list..."
    response=$(curl -s -X POST "$SERVER_URL/rpc" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }')
    
    if echo "$response" | grep -q '"result"'; then
        print_success "Tools list successful"
        tool_count=$(echo "$response" | jq '.result.tools | length' 2>/dev/null || echo "unknown")
        print_status "Found $tool_count tools"
    else
        print_error "Tools list failed: $response"
        return 1
    fi
    
    # Test tool call
    print_status "Testing tool call..."
    response=$(curl -s -X POST "$SERVER_URL/rpc" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "filter_Alphabetical_list_of_products_for_NorthSvc",
                "arguments": {
                    "$top": 3
                }
            }
        }')
    
    if echo "$response" | grep -q '"result"'; then
        print_success "Tool call successful"
        echo "$response" | jq '.result.content[0].text' 2>/dev/null || echo "$response"
    else
        print_error "Tool call failed: $response"
        return 1
    fi
}

# Function to test error handling
test_errors() {
    print_status "Testing error handling..."
    
    # Test invalid JSON
    response=$(curl -s -X POST "$SERVER_URL/rpc" \
        -H "Content-Type: application/json" \
        -d 'invalid json')
    
    if echo "$response" | grep -q '"error"'; then
        print_success "Invalid JSON handled correctly"
    else
        print_error "Invalid JSON not handled properly: $response"
    fi
    
    # Test non-existent tool
    response=$(curl -s -X POST "$SERVER_URL/rpc" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool",
                "arguments": {}
            }
        }')
    
    if echo "$response" | grep -q '"error"'; then
        print_success "Non-existent tool handled correctly"
    else
        print_error "Non-existent tool not handled properly: $response"
    fi
}

# Function to test different ports
test_different_ports() {
    print_status "Testing different port configurations..."
    
    # Test custom port
    $BINARY --transport http --http-addr localhost:3000 "$ODATA_SERVICE" > server_custom.log 2>&1 &
    CUSTOM_PID=$!
    
    sleep 2
    
    if curl -s "http://localhost:3000/health" > /dev/null 2>&1; then
        print_success "Custom port (3000) working"
    else
        print_error "Custom port (3000) failed"
    fi
    
    kill $CUSTOM_PID 2>/dev/null || true
    wait $CUSTOM_PID 2>/dev/null || true
}

# Function to test security restrictions
test_security() {
    print_status "Testing security restrictions..."
    
    # Test that server doesn't start on 0.0.0.0 without expert flag
    print_status "Testing that server refuses to bind to 0.0.0.0 without expert flag..."
    
    # This should fail
    if timeout 5s $BINARY --transport http --http-addr 0.0.0.0:8080 "$ODATA_SERVICE" > security_test.log 2>&1; then
        print_error "Server started on 0.0.0.0 without expert flag (security issue!)"
        return 1
    else
        print_success "Server correctly refused to bind to 0.0.0.0 without expert flag"
    fi
    
    # Test with expert flag (should work but warn)
    print_status "Testing with expert flag..."
    $BINARY --transport http --http-addr 0.0.0.0:8080 --i-am-security-expert-i-know-what-i-am-doing "$ODATA_SERVICE" > security_expert.log 2>&1 &
    EXPERT_PID=$!
    
    sleep 2
    
    if curl -s "http://localhost:8080/health" > /dev/null 2>&1; then
        print_success "Server started with expert flag"
    else
        print_error "Server failed to start with expert flag"
    fi
    
    kill $EXPERT_PID 2>/dev/null || true
    wait $EXPERT_PID 2>/dev/null || true
}

# Function to run all tests
run_all_tests() {
    print_status "Starting comprehensive HTTP transport tests..."
    
    # Start server
    if ! start_server; then
        print_error "Failed to start server"
        exit 1
    fi
    
    # Run tests
    test_health
    test_sse
    test_rpc
    test_errors
    
    # Stop server
    stop_server
    
    # Test different configurations
    test_different_ports
    test_security
    
    print_success "All HTTP transport tests completed!"
}

# Function to show usage
show_usage() {
    echo "OData MCP HTTP Transport Test Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --health     Test only health endpoint"
    echo "  --sse        Test only SSE connection"
    echo "  --rpc        Test only RPC endpoint"
    echo "  --errors     Test only error handling"
    echo "  --security   Test only security restrictions"
    echo "  --all        Run all tests (default)"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 --health           # Test only health endpoint"
    echo "  $0 --rpc              # Test only RPC functionality"
}

# Main script
case "${1:-all}" in
    --health)
        start_server && test_health && stop_server
        ;;
    --sse)
        start_server && test_sse && stop_server
        ;;
    --rpc)
        start_server && test_rpc && stop_server
        ;;
    --errors)
        start_server && test_errors && stop_server
        ;;
    --security)
        test_security
        ;;
    --all|all)
        run_all_tests
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

# Cleanup
rm -f server.log server_custom.log security_test.log security_expert.log sse_output.log

print_success "HTTP transport testing completed!" 