@echo off
TITLE Docker MCP Gateway - Port 3000
echo Starting Docker MCP Gateway on port 3000...
echo This will take a moment to initialize...
echo Press Ctrl+C to stop the gateway

echo.
echo ================================================================
echo DOCKER MCP GATEWAY IS NOW RUNNING ON PORT 3000
echo Keep this window open while using the MCP toolkit
echo ================================================================
echo.

"C:\Program Files\Docker\Docker\resources\bin\docker.exe" mcp gateway run --port 3000 --transport http

echo.
echo Docker MCP Gateway has stopped.
pause