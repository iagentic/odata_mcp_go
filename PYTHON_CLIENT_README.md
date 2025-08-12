# OData MCP OpenAI Python Client

This Python client demonstrates how to use OpenAI with the OData MCP server to query and analyze OData services through natural language.

## Features

- 🤖 **AI-Powered Queries**: Use natural language to query OData services
- 🔧 **Automatic Tool Selection**: AI automatically chooses the right MCP tools
- 📊 **Real-time Data**: Get live data from OData services
- 💬 **Interactive Mode**: Chat with your OData service
- 🔄 **Batch Processing**: Execute multiple queries programmatically

## Prerequisites

1. **OData MCP Server**: Must be running with HTTP transport
2. **OpenAI API Key**: Required for AI functionality
3. **Python 3.7+**: For running the client

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Start the OData MCP server**:
   ```bash
   ./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/
   ```

## Usage

### Interactive Mode

Run the client in interactive mode to chat with your OData service:

```bash
python mcp_openai_client.py
```

Example session:
```
🚀 OData MCP OpenAI Client
==================================================

✅ Health check passed
✅ MCP initialization successful
✅ Loaded 157 tools

💡 Available tools:
- odata_service_info_for_NorthSvc: Get metadata and capabilities of the OData service
- filter_Alphabetical_list_of_products_for_NorthSvc: Filter Alphabetical list of products entities (parameters: $top, $skip, $filter, $select, $orderby, $expand)
- count_Alphabetical_list_of_products_for_NorthSvc: Get count of Alphabetical list of products entities (parameters: $filter)
...

==================================================
💬 Ask questions about the OData service (type 'quit' to exit)
Examples:
- 'Show me the first 5 products'
- 'Get information about categories'
- 'Find products with price less than 20'
==================================================

🤔 Your query: Show me the first 3 products

🔄 Processing...

🤖 AI Explanation: I'm querying the Products entity to get a list of products
🔧 Tool: filter_Alphabetical_list_of_products_for_NorthSvc
📝 Arguments: {'$top': 3}
💭 Reasoning: The user wants to see products, so I'll use the filter tool with a limit of 3 items

✅ Tool executed successfully:

{"@odata.count":69,"value":[{"CategoryID":1,"CategoryName":"Beverages","Discontinued":false,"ProductID":1,"ProductName":"Chai","QuantityPerUnit":"10 boxes x 20 bags","ReorderLevel":10,"SupplierID":1,"UnitPrice":"18.0000","UnitsInStock":39,"UnitsOnOrder":0},{"CategoryID":1,"CategoryName":"Beverages","Discontinued":false,"ProductID":2,"ProductName":"Chang","QuantityPerUnit":"24 - 12 oz bottles","ReorderLevel":25,"SupplierID":1,"UnitPrice":"19.0000","UnitsInStock":17,"UnitsOnOrder":40},{"CategoryID":1,"CategoryName":"Beverages","Discontinued":false,"ProductID":34,"ProductName":"Sasquatch Ale","QuantityPerUnit":"24 - 12 oz bottles","ReorderLevel":15,"SupplierID":16,"UnitPrice":"14.0000","UnitsInStock":111,"UnitsOnOrder":0}]}
```

### Single Query Mode

Execute a single query:

```bash
python mcp_openai_client.py --query "Show me products with price less than 20"
```

### Custom Configuration

```bash
# Custom MCP server URL
python mcp_openai_client.py --mcp-url http://localhost:3000

# Custom OpenAI model
python mcp_openai_client.py --model gpt-3.5-turbo

# Custom OpenAI API key
python mcp_openai_client.py --openai-key "your-key-here"
```

### Programmatic Usage

```python
from mcp_openai_client import MCPOpenAIClient

# Create client
client = MCPOpenAIClient()

# Initialize connection
if client.initialize_mcp():
    # Query with AI
    result = client.query_with_openai("Show me the first 5 products")
    print(result)
    
    # Call specific tool
    result = client.call_tool(
        "filter_Alphabetical_list_of_products_for_NorthSvc",
        {"$top": 3}
    )
    print(result)
```

## Example Queries

### Basic Queries
- "Show me the first 5 products"
- "Get information about categories"
- "How many products are there?"
- "Show me products from the Beverages category"

### Filtered Queries
- "Find products with price less than 20"
- "Show me discontinued products"
- "Get products with stock less than 10"
- "Find products from supplier 1"

### Complex Queries
- "Show me products with their category information"
- "Get products ordered by price descending"
- "Find products with price between 10 and 50"

## How It Works

1. **Initialization**: Connects to the MCP server and loads available tools
2. **Query Processing**: Sends natural language query to OpenAI
3. **Tool Selection**: AI determines which MCP tool to use and with what parameters
4. **Execution**: Calls the selected tool with the specified parameters
5. **Response**: Returns the formatted results

### AI Prompt Structure

The AI receives a system prompt that includes:
- List of all available MCP tools with descriptions
- Tool parameters and capabilities
- Instructions to return JSON with tool selection and reasoning

### Tool Selection Logic

The AI analyzes the user query and:
1. Identifies the relevant entity (Products, Categories, etc.)
2. Determines the operation type (filter, get, count, etc.)
3. Extracts relevant parameters ($top, $filter, etc.)
4. Returns the exact tool name and arguments

## Error Handling

The client handles various error scenarios:

- **Connection Issues**: Checks MCP server health before operations
- **Tool Not Found**: Provides helpful error messages
- **Invalid Parameters**: Validates tool arguments
- **OpenAI API Errors**: Graceful handling of API failures
- **JSON Parsing Errors**: Fallback to text-based tool selection

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `MCP_SERVER_URL`: MCP server URL (default: http://localhost:8080)

### Command Line Arguments
- `--mcp-url`: MCP server URL
- `--openai-key`: OpenAI API key
- `--query`: Single query to execute
- `--model`: OpenAI model to use (default: gpt-4)

## Troubleshooting

### Common Issues

1. **"Health check failed"**
   - Ensure the MCP server is running
   - Check the server URL is correct
   - Verify the server is using HTTP transport

2. **"OpenAI API key required"**
   - Set the OPENAI_API_KEY environment variable
   - Or use the --openai-key argument

3. **"Tool not found"**
   - Check that the MCP server has loaded the OData service
   - Verify the tool name matches exactly

4. **"MCP initialization failed"**
   - Ensure the MCP server is accessible
   - Check for network connectivity issues

### Debug Mode

Enable verbose output by modifying the client:

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

### Custom Tool Descriptions

You can customize how tools are described to the AI:

```python
def get_tool_descriptions(self) -> str:
    # Custom formatting for better AI understanding
    descriptions = []
    for tool in self.tools:
        if "filter" in tool.name.lower():
            desc = f"Query {tool.name}: {tool.description}"
        elif "count" in tool.name.lower():
            desc = f"Count {tool.name}: {tool.description}"
        else:
            desc = f"Get {tool.name}: {tool.description}"
        descriptions.append(desc)
    return "\n".join(descriptions)
```

### Batch Processing

Process multiple queries:

```python
queries = [
    "Show me the first 5 products",
    "Get category information",
    "Find expensive products"
]

for query in queries:
    result = client.query_with_openai(query)
    print(f"Query: {query}")
    print(f"Result: {result}")
    print("-" * 50)
```

### Custom OpenAI Models

Use different OpenAI models:

```python
# Use GPT-3.5 for faster responses
result = client.query_with_openai("Show me products", model="gpt-3.5-turbo")

# Use GPT-4 for complex queries
result = client.query_with_openai("Analyze product pricing trends", model="gpt-4")
```

## Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Network Security**: Use HTTPS for production deployments
- **Access Control**: Implement proper authentication for production use
- **Rate Limiting**: Be aware of OpenAI API rate limits

## Performance Tips

1. **Cache Tool Descriptions**: Store tool information to avoid repeated API calls
2. **Batch Queries**: Process multiple queries in a single session
3. **Use Appropriate Models**: GPT-3.5-turbo for simple queries, GPT-4 for complex ones
4. **Connection Pooling**: Reuse HTTP connections when possible

## Integration Examples

### Web Application

```python
from flask import Flask, request, jsonify
from mcp_openai_client import MCPOpenAIClient

app = Flask(__name__)
client = MCPOpenAIClient()

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    result = client.query_with_openai(user_query)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
```

### Jupyter Notebook

```python
# In a Jupyter notebook
from mcp_openai_client import MCPOpenAIClient

client = MCPOpenAIClient()
client.initialize_mcp()

# Interactive queries
result = client.query_with_openai("Show me the top 10 products by price")
print(result)
```

## Contributing

To contribute to this client:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 