FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY tron_mcp_server/ ./tron_mcp_server/

# Default: stdio mode; append --sse to enable SSE mode
# stdio:  docker run --env-file .env tron-mcp-server
# SSE:    docker run --env-file .env -p 8765:8765 tron-mcp-server --sse
ENTRYPOINT ["python", "-m", "tron_mcp_server.server"]
