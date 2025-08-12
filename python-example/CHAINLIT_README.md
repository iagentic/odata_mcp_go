# Chainlit Web Applications for OData MCP

This directory contains Chainlit web applications that provide a user-friendly web interface for querying OData services using natural language.

## Applications

### 1. Basic Chainlit App (`chainlit_app.py`)
A simple web interface for the OData MCP OpenAI client.

**Features:**
- Natural language query processing
- Real-time chat interface
- Settings configuration
- Error handling

### 2. Advanced Chainlit App (`chainlit_advanced_app.py`)
Enhanced version with data visualization and advanced features.

**Features:**
- Data table visualization
- JSON parsing and formatting
- Tool categorization display
- Summary statistics
- Debug information
- Better error handling

## Prerequisites

1. **OData MCP Server**: Must be running with HTTP transport
2. **OpenAI API Key**: Required for AI functionality
3. **Python 3.7+**: For running the applications

## Installation

1. **Install dependencies**:
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

### Running the Basic App

```bash
chainlit run chainlit_app.py
```

### Running the Advanced App

```bash
chainlit run chainlit_advanced_app.py
```

The application will start and be available at `http://localhost:8000`.

## Features

### Web Interface
- **Real-time Chat**: Interactive chat interface
- **Settings Panel**: Configure API keys and server URLs
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Graceful error messages and recovery

### Data Visualization (Advanced App)
- **Data Tables**: Automatic table generation from OData responses
- **Summary Statistics**: Record counts and column information
- **JSON Parsing**: Automatic parsing of OData JSON responses
- **Debug Information**: Raw response display for troubleshooting

### Configuration Options
- **OpenAI API Key**: Set via environment variable or settings
- **MCP Server URL**: Customize server endpoint
- **OpenAI Model**: Choose between GPT-4, GPT-3.5-turbo, etc.
- **Max Records**: Control how many records to display

## Example Queries

### Basic Queries
- "Show me the first 5 products"
- "Get information about categories"
- "How many products are there?"
- "Show me products from the Beverages category"

### Advanced Queries
- "Find products with price less than 20"
- "Show me discontinued products"
- "Get products with stock less than 10"
- "Create a table of products with their prices"

### Complex Queries
- "Show me products with their category information"
- "Get products ordered by price descending"
- "Find products with price between 10 and 50"

## Screenshots

### Basic App
```
🚀 OData MCP Chat
==================================================

✅ Connected successfully!

📊 Loaded 157 tools from the OData service

💡 Available operations:
- Query products, categories, suppliers, and more
- Filter data with natural language
- Get counts and statistics
- Search and sort data

💬 Try asking questions like:
- "Show me the first 5 products"
- "Find products with price less than 20"
- "Get information about categories"
- "How many products are there?"
- "Show me products from the Beverages category"

🤔 Your query: Show me the first 3 products

📊 Result:
{"@odata.count":69,"value":[{"ProductID":1,"ProductName":"Chai",...}]}
```

### Advanced App
```
📊 Data retrieved successfully!

📈 Summary:
- Records: 3
- Columns: 10
- Columns: ProductID, ProductName, CategoryID, CategoryName, Discontinued, SupplierID, UnitPrice, UnitsInStock, UnitsOnOrder, ReorderLevel

[Data Table Display]

📝 Showing first 10 of 3 records. Use filters to see more specific data.

🔍 Raw Response:
{"@odata.count":69,"value":[...]}
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `MCP_SERVER_URL`: MCP server URL (default: http://localhost:8080)

### Settings Panel
Access the settings panel in the web interface to configure:
- OpenAI API Key
- MCP Server URL
- OpenAI Model
- Max Records to Display

## Troubleshooting

### Common Issues

1. **"OpenAI API key required"**
   - Set the `OPENAI_API_KEY` environment variable
   - Or provide it in the settings panel

2. **"Failed to connect to MCP server"**
   - Ensure the OData MCP server is running
   - Check the server URL in settings
   - Verify the server is using HTTP transport

3. **"Client not initialized"**
   - Restart the chat session
   - Check the MCP server connection

4. **Data not displaying properly**
   - Check the raw JSON response in debug info
   - Verify the OData service is returning valid JSON
   - Try simpler queries first

### Debug Mode

Enable debug logging by adding to your Python script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Customizing the Apps

1. **Add New Features**:
   ```python
   # Add custom data processing
   def custom_data_processor(data):
       # Your custom logic here
       return processed_data
   ```

2. **Modify UI Elements**:
   ```python
   # Custom page configuration
   cl.set_page_config(
       page_title="Custom Title",
       page_icon="🚀",
       layout="wide"
   )
   ```

3. **Add New Settings**:
   ```python
   cl.set_settings([
       cl.Setting(
           id="custom_setting",
           label="Custom Setting",
           type="text",
           default="default_value"
       )
   ])
   ```

### Extending Functionality

1. **Add Data Visualization**:
   ```python
   import plotly.express as px
   
   # Create charts
   fig = px.bar(df, x='CategoryName', y='UnitPrice')
   await cl.Message(content=fig.to_html()).send()
   ```

2. **Add Export Features**:
   ```python
   # Export to CSV
   csv_data = df.to_csv(index=False)
   await cl.Message(content=csv_data, author="CSV Export").send()
   ```

3. **Add Multi-step Queries**:
   ```python
   # Chain multiple queries
   result1 = client.query_with_openai("Get products")
   result2 = client.query_with_openai("Filter by price > 20")
   ```

## Deployment

### Local Development
```bash
chainlit run chainlit_app.py --port 8000
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn chainlit_app:app --bind 0.0.0.0:8000

# Using Docker
docker build -t chainlit-app .
docker run -p 8000:8000 chainlit-app
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-key"
export MCP_SERVER_URL="http://your-server:8080"
export CHAINLIT_HOST="0.0.0.0"
export CHAINLIT_PORT="8000"
```

## Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Network Security**: Use HTTPS for production deployments
- **Access Control**: Implement authentication for production use
- **Rate Limiting**: Be aware of OpenAI API rate limits

## Performance Tips

1. **Cache Tool Descriptions**: Store tool information to avoid repeated API calls
2. **Batch Queries**: Process multiple queries in a single session
3. **Use Appropriate Models**: GPT-3.5-turbo for simple queries, GPT-4 for complex ones
4. **Connection Pooling**: Reuse HTTP connections when possible

## Integration Examples

### With Other Web Frameworks
```python
# Flask integration
from flask import Flask
from chainlit_app import mcp_client

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    result = mcp_client.query_with_openai(user_query)
    return jsonify({'result': result})
```

### With Data Analysis Tools
```python
# Jupyter integration
import chainlit as cl
from mcp_openai_client import MCPOpenAIClient

client = MCPOpenAIClient()
client.initialize_mcp()

# Use in Jupyter notebooks
result = client.query_with_openai("Show me product statistics")
```

## Contributing

To contribute to these applications:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 