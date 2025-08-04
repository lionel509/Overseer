# Overseer API Documentation

The Overseer API provides REST endpoints for all CLI tools and system management functionality.

## Quick Start

### Installation

```bash
cd backend/api
pip install -r requirements.txt
```

### Running the API Server

```bash
python main.py --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```bash
python main.py --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoints

#### `GET /`
Get API information and available endpoints.

#### `GET /api/health`
Health check endpoint.

#### `GET /api/tools`
List all available tools.

### System Endpoints

#### `GET /api/system/info`
Get system information (platform, architecture, etc.).

#### `GET /api/system/memory`
Get memory usage information.

#### `GET /api/system/disk`
Get disk usage information.

#### `GET /api/system/network`
Get network status information.

#### `GET /api/system/processes`
Get list of running processes.

### File Search Endpoints

#### `POST /api/tools/file-search/search`
Search for files with advanced filtering.

**Request Body:**
```json
{
  "query": "*.py",
  "base_path": "/",
  "recursive": true,
  "file_types": [".py", ".js"],
  "size_range": {"min": 0, "max": 1000000},
  "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
  "include_hidden": false,
  "search_in_content": false
}
```

#### `GET /api/tools/file-search/history`
Get file search history.

#### `DELETE /api/tools/file-search/history`
Clear file search history.

#### `GET /api/tools/file-search/content/{file_path}`
Get file content (first N lines).

### Command Processor Endpoints

#### `POST /api/tools/command-processor/execute`
Execute a command.

**Request Body:**
```json
{
  "command": "system_info",
  "args": []
}
```

#### `GET /api/tools/command-processor/history`
Get command execution history.

#### `DELETE /api/tools/command-processor/history`
Clear command history.

#### `GET /api/tools/command-processor/supported`
Get list of supported commands.

### Tool Recommender Endpoints

#### `GET /api/tools/tool-recommender/recommendations`
Get tool recommendations based on system context.

#### `GET /api/tools/tool-recommender/context`
Get current system context.

#### `POST /api/tools/tool-recommender/usage/{tool_id}`
Record tool usage.

#### `GET /api/tools/tool-recommender/usage`
Get tool usage statistics.

#### `GET /api/tools/tool-recommender/tools`
Get list of available tools.

#### `GET /api/tools/tool-recommender/categories`
Get list of tool categories.

#### `GET /api/tools/tool-recommender/tools/category/{category}`
Get tools by category.

### Real-Time Stats Endpoints

#### `POST /api/tools/real-time-stats/start`
Start real-time monitoring.

**Request Body:**
```json
{
  "interval": 2.0,
  "max_data_points": 100
}
```

#### `POST /api/tools/real-time-stats/stop`
Stop real-time monitoring.

#### `GET /api/tools/real-time-stats/status`
Get monitoring status.

#### `GET /api/tools/real-time-stats/current`
Get current system statistics.

#### `GET /api/tools/real-time-stats/history`
Get statistics history.

#### `GET /api/tools/real-time-stats/summary`
Get statistics summary.

#### `GET /api/tools/real-time-stats/thresholds`
Get alert thresholds.

#### `PUT /api/tools/real-time-stats/thresholds`
Set alert thresholds.

**Request Body:**
```json
{
  "cpu_warning": 60.0,
  "cpu_critical": 80.0,
  "memory_warning": 70.0,
  "memory_critical": 85.0,
  "disk_warning": 80.0,
  "disk_critical": 90.0
}
```

#### `DELETE /api/tools/real-time-stats/history`
Clear statistics history.

## Example Usage

### Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get system info
response = requests.get(f"{BASE_URL}/api/system/info")
system_info = response.json()
print(f"Platform: {system_info['platform']}")

# Search for files
search_data = {
    "query": "*.py",
    "base_path": "/",
    "recursive": True,
    "file_types": [".py"]
}
response = requests.post(f"{BASE_URL}/api/tools/file-search/search", json=search_data)
search_results = response.json()
print(f"Found {len(search_results['data'])} files")

# Get tool recommendations
response = requests.get(f"{BASE_URL}/api/tools/tool-recommender/recommendations")
recommendations = response.json()
for rec in recommendations['data']:
    print(f"- {rec['name']}: {rec['reason']}")

# Start monitoring
monitoring_data = {"interval": 2.0}
response = requests.post(f"{BASE_URL}/api/tools/real-time-stats/start", json=monitoring_data)
print("Monitoring started")

# Get current stats
response = requests.get(f"{BASE_URL}/api/tools/real-time-stats/current")
stats = response.json()
print(f"CPU: {stats['cpu']['usage']}%, Memory: {stats['memory']['percent']}%")
```

### cURL Examples

```bash
# Get system info
curl http://localhost:8000/api/system/info

# Search for files
curl -X POST http://localhost:8000/api/tools/file-search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "*.py", "recursive": true}'

# Get tool recommendations
curl http://localhost:8000/api/tools/tool-recommender/recommendations

# Start monitoring
curl -X POST http://localhost:8000/api/tools/real-time-stats/start \
  -H "Content-Type: application/json" \
  -d '{"interval": 2.0}'

# Get current stats
curl http://localhost:8000/api/tools/real-time-stats/current
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable (tool not available)

Error responses include:
```json
{
  "error": "Error message",
  "detail": "Additional error details"
}
```

## Authentication

Currently, the API runs without authentication. For production use, consider adding:

- API key authentication
- JWT tokens
- OAuth2 integration

## Rate Limiting

Consider implementing rate limiting for production use:

- Per-endpoint limits
- Per-client limits
- Burst protection

## Monitoring

The API includes built-in monitoring:

- Health check endpoint
- Request logging
- Error tracking
- Performance metrics

## Development

### Adding New Endpoints

1. Create a new router in `routes.py`
2. Define Pydantic models for request/response validation
3. Implement the endpoint logic
4. Include the router in the main app

### Testing

Run the test suite:

```bash
python -m pytest tests/
```

### Deployment

For production deployment:

1. Use a production ASGI server (Gunicorn + Uvicorn)
2. Configure reverse proxy (Nginx)
3. Set up SSL/TLS certificates
4. Implement proper logging
5. Add monitoring and alerting

## Tools Overview

### File Search Tool
- Advanced file search with pattern matching
- Filtering by file type, size, date
- Content search capabilities
- Search history management

### Command Processor Tool
- Execute system commands
- Built-in system information commands
- Command history tracking
- Supported commands listing

### Tool Recommender Tool
- Context-aware tool recommendations
- System state analysis
- Usage tracking and statistics
- Tool categorization

### Real-Time Stats Tool
- Live system monitoring
- Performance metrics collection
- Alert threshold management
- Historical data analysis

## License

This API is part of the Overseer project and follows the same license terms. 