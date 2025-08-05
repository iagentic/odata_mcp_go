# API Key Authentication Support

## 🎯 New Feature: API Key Authentication

The Go MCP server now supports **API key authentication** for OData services that require API keys instead of username/password authentication.

## ✅ Supported Authentication Methods

The server now supports multiple authentication methods:

1. **Basic Authentication** (username/password)
2. **API Key Authentication** (NEW!)
3. **Cookie Authentication** (cookie file or cookie string)
4. **CSRF Token handling** (for SAP services)

## 🚀 Usage Examples

### **Command Line Usage:**

```bash
# API Key via command line
./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/

# API Key via environment variable
export ODATA_API_KEY="W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga"
./odata-mcp https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/

# Alternative environment variable name
export APIKEY="W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga"
./odata-mcp https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/
```

### **HTTP Transport Usage:**

```bash
# Start server with API key
./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/

# Then use with Python client
python mcp_openai_client.py
```

## 🔧 Implementation Details

### **Header Format:**
The API key is sent as an HTTP header:
```
apikey: W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga
```

### **Code Changes:**

1. **ODataClient** (`internal/client/client.go`):
   ```go
   type ODataClient struct {
       // ... existing fields ...
       apiKey string
   }
   
   func (c *ODataClient) SetAPIKey(apiKey string) {
       c.apiKey = apiKey
   }
   ```

2. **Constants** (`internal/constants/constants.go`):
   ```go
   const (
       APIKeyHeader = "apikey"
   )
   ```

3. **Config** (`internal/config/config.go`):
   ```go
   type Config struct {
       // ... existing fields ...
       APIKey string `mapstructure:"api_key"`
   }
   
   func (c *Config) HasAPIKey() bool {
       return c.APIKey != ""
   }
   ```

4. **Command Line** (`cmd/odata-mcp/main.go`):
   ```go
   rootCmd.Flags().StringVar(&cfg.APIKey, "api-key", "", "API key for authentication")
   rootCmd.Flags().StringVar(&cfg.APIKey, "apikey", "", "API key for authentication (alias)")
   ```

## 📋 Command Line Options

### **API Key Flags:**
- `--api-key <key>` - Set API key for authentication
- `--apikey <key>` - Alias for --api-key

### **Environment Variables:**
- `ODATA_API_KEY` - API key for authentication
- `APIKEY` - Alternative environment variable name

### **Mutual Exclusivity:**
Only one authentication method can be used at a time:
- Basic Auth (username/password)
- API Key
- Cookie Authentication

## 🔍 Example with SAP C4C API

### **Your Original curl Command:**
```bash
curl -H "apikey: W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga" \
     "https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/ContactCollection?$top=50&$inlinecount=allpages"
```

### **Equivalent MCP Command:**
```bash
./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/
```

### **Then Query via MCP:**
```python
# Using the Python client
client = MCPOpenAIClient()
result = client.query_with_openai("Show me the first 50 contacts")
```

## 🎯 Benefits

### **✅ For SAP C4C API:**
- **Direct API Key Support** - No need for username/password
- **Sandbox Access** - Works with SAP sandbox environments
- **OData v2 Compatibility** - Full OData v2 feature support
- **MCP Integration** - Seamless integration with AI assistants

### **✅ For Other APIs:**
- **Universal Support** - Works with any OData service using API keys
- **Flexible Authentication** - Multiple authentication methods
- **Environment Variables** - Secure credential management
- **Command Line Options** - Easy integration into scripts

## 🔒 Security Considerations

### **Environment Variables (Recommended):**
```bash
# Set API key securely
export ODATA_API_KEY="your-api-key-here"

# Use without exposing key in command line
./odata-mcp https://your-odata-service.com/
```

### **Command Line (Less Secure):**
```bash
# Key visible in process list
./odata-mcp --api-key your-api-key-here https://your-odata-service.com/
```

## 🚀 Quick Start

### **1. Set API Key:**
```bash
export ODATA_API_KEY="W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga"
```

### **2. Start MCP Server:**
```bash
./odata-mcp --transport http https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi/
```

### **3. Test with Python Client:**
```bash
cd python-example
python mcp_openai_client.py
```

### **4. Query Examples:**
```
User: "Show me the first 10 contacts"
User: "Get contact details for contact ID 12345"
User: "Find contacts with email containing 'test'"
```

## 📊 Supported OData Services

This feature works with any OData service that accepts API key authentication, including:

- **SAP C4C API** (Customer Experience)
- **SAP S/4HANA Cloud**
- **Microsoft Dynamics 365**
- **Salesforce OData**
- **Custom OData Services**

## 🔧 Troubleshooting

### **Common Issues:**

1. **"Invalid API Key"**:
   - Verify the API key is correct
   - Check if the service requires a different header name
   - Ensure the API key has proper permissions

2. **"Authentication Required"**:
   - Make sure you're using the correct authentication method
   - Check if the service requires additional headers

3. **"Service Not Found"**:
   - Verify the OData service URL is correct
   - Check if the service is accessible from your network

### **Debug Mode:**
```bash
# Enable verbose output for debugging
./odata-mcp --verbose --api-key your-key https://your-service.com/
```

## 🎯 Conclusion

The API key authentication feature makes it easy to connect to OData services that require API key authentication, such as SAP C4C and other cloud-based OData services. This provides a secure and convenient way to access these services through the MCP bridge. 