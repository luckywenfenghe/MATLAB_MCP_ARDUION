# MATLAB MCP Integration

This is an implementation of a Model Context Protocol (MCP) server for MATLAB. It allows MCP clients (like LLM agents or Claude Desktop) to interact with a shared MATLAB session using the MATLAB Engine API for Python.

## Features

*   **Execute MATLAB Code:** Run arbitrary MATLAB code snippets via the `runMatlabCode` tool.
*   **Retrieve Variables:** Get the value of variables from the MATLAB workspace using the `getVariable` tool.
*   **Auto-Start MATLAB:** Automatically starts MATLAB and shares engine if no shared sessions are found.
*   **Batch Script Support:** Convenient Windows batch files for one-click startup.
*   **Structured Communication:** Tools return results and errors as structured JSON for easier programmatic use by clients.
*   **Non-Blocking Execution:** MATLAB engine calls are run asynchronously using `asyncio.to_thread` to prevent blocking the server.
*   **Standard Logging:** Uses Python's standard `logging` module, outputting to `stderr` for visibility in client logs.
*   **Shared Session:** Connects to an existing shared MATLAB session.

### TODO:

*   Add a `setVariable` tool to write data to the MATLAB workspace.
*   Add a `runScript` tool to execute `.m` files directly.
*   Add tools for workspace management (e.g., `clearWorkspace`, `getWorkspaceVariables`).
*   Expand `matlab_to_python` helper to handle more complex data types (structs, cell arrays, objects).
*   Add support for interacting with Simulink models.

## Requirements

*   Python 3.12 or higher
*   MATLAB (**R2023a or higher recommended** - check MATLAB Engine API for Python compatibility) with the MATLAB Engine API for Python installed.
*   `numpy` Python package.

## Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/luckywenfenghe/MATLAB_MCP_ARDUION.git
    cd MatlabMCP
    ```

2.  Set up a Python virtual environment (recommended):
    ```bash
    # Install uv if you haven't already: https://github.com/astral-sh/uv
    uv init
    uv venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    uv pip sync
    ```

4.  Ensure MATLAB is installed and the MATLAB Engine API for Python is configured for your Python environment. See [MATLAB Documentation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

5.  **Auto-start MATLAB (Recommended):** You can now use one of the provided batch files to automatically start MATLAB and the MCP server:
    
    **Simple start:**
    ```batch
    start_matlab_mcp.bat
    ```
    
    **Advanced start with detailed checks:**
    ```batch
    start_matlab_mcp_advanced.bat
    ```
    
    **PowerShell version:**
    ```powershell
    .\start_matlab_mcp.ps1
    ```
    
    **Manual start (if auto-start doesn't work):** Run the following command in the MATLAB Command Window:
    ```matlab
    matlab.engine.shareEngine
    ```
    You can verify it's shared by running `matlab.engine.isEngineShared` in MATLAB (it should return `true` or `1`). The MCP server needs this shared engine to connect.

## Configuration (for Claude Desktop)

To use this server with Claude Desktop:

1.  Go to Claude Desktop -> Settings -> Developer -> Edit Config.
2.  This will open `claude_desktop_config.json`. Add or modify the `mcpServers` section to include the `MatlabMCP` configuration:

    ```json
    {
      "mcpServers": {
        "MatlabMCP": {
          "command": "C:\\Users\\username\\.local\\bin\\uv.exe", // Path to your uv executable
          "args": [
            "--directory",
            "C:\\Users\\username\\Desktop\\MatlabMCP\\", // ABSOLUTE path to the cloned repository directory
            "run",
            "main.py"
          ]
          // Optional: Add environment variables if needed
          // "env": {
          //   "MY_VAR": "value"
          // }
        }
        // Add other MCP servers here if you have them
      }
    }
    ```
3.  **IMPORTANT:** Replace `C:\\Users\\username\\...` paths with the correct **absolute paths** for your system.
4.  Save the file and **restart Claude Desktop**.
5.  **Logging:** Server logs (from Python's `logging` module) will appear in Claude Desktop's MCP log files (accessible via `tail -f ~/Library/Logs/Claude/mcp-server-MatlabMCP.log` on macOS or checking `%APPDATA%\Claude\logs\` on Windows).

## Quick Start Guide

### Option 1: Auto-Start (Recommended)
1. Double-click `start_matlab_mcp_advanced.bat` for a full automated startup with status checks.
2. The script will:
   - Check MATLAB installation
   - Verify Python environment
   - Start MATLAB and share its engine
   - Launch the MCP server
   - Show detailed progress information

### Option 2: Simple Auto-Start
1. Double-click `start_matlab_mcp.bat` for a quick startup.
2. Wait for MATLAB to start and the MCP server to connect.

### Option 2.1: PowerShell Auto-Start
1. Right-click on `start_matlab_mcp.ps1` and select "Run with PowerShell".
2. Or run `.\start_matlab_mcp.ps1` in PowerShell terminal.
3. Includes colored output and better error handling.

### Option 3: Manual Start
1. Start MATLAB manually
2. Run `matlab.engine.shareEngine` in MATLAB Command Window
3. Run `python main.py` in the project directory

### Troubleshooting
- If MATLAB is not found in PATH, add MATLAB installation directory to your system PATH
- If virtual environment is missing, run `uv venv` first
- If connection fails, ensure MATLAB is running and engine is shared
- Check log files for detailed error information


## Development

Project Structure:
```
MatlabMCP/
├── .venv/                     # Virtual environment created by uv
├── Docs/
│   └── Images/
│   └── Updates.md             # Documentation for updates and changes
├── main.py                    # The MCP server script
├── pyproject.toml             # Project metadata and dependencies
├── README.md                  # This file
└── uv.lock                    # Lock file for dependencies
```

## Documentation
Check out [Updates](./Docs/Updates.md) for detailed documentation on the server's features, usage, and development notes.

## Contributing
Contributions are welcome! If you have any suggestions or improvements, feel free to open an issue or submit a pull request.

Let's make this even better together!
