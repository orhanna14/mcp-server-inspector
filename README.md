# MCP Server Inspector

A comprehensive tool for inspecting, testing, and developing MCP (Model Context Protocol) servers with an enhanced multi-server chatbot.

## 🚀 Features

- **MCP Server Inspector**: Web-based interface for testing MCP servers
- **Multi-Server Chatbot**: AI-powered chatbot that connects to multiple MCP servers simultaneously
- **Research Server**: Custom MCP server for searching academic papers on arXiv
- **Filesystem Integration**: File and directory operations through MCP
- **Web Content Fetching**: Retrieve and process web content via MCP

## 📁 Project Structure

```
mcp-server-inspector/
├── mcp_project/                 # Main MCP implementation
│   ├── mcp_chatbot.py          # Multi-server MCP chatbot
│   ├── research_server.py       # Custom research MCP server
│   ├── server_config.json       # Server configuration
│   ├── pyproject.toml          # Python dependencies
│   └── papers/                 # Stored research papers
├── main.py                     # MCP inspector launcher
├── launch_inspector.py         # Alternative inspector launcher
├── mcp_server.py               # MCP server implementation
└── pyproject.toml             # Root project configuration
```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mcp-server-inspector
   ```

2. **Install dependencies:**
   ```bash
   # Install root dependencies
   uv sync
   
   # Install mcp_project dependencies
   cd mcp_project
   uv sync
   ```

3. **Install Node.js** (required for MCP inspector and filesystem server):
   ```bash
   # Download from https://nodejs.org/
   # or use your package manager
   ```

## 🎯 Usage

### Option 1: MCP Server Inspector

Launch the web-based inspector to test MCP servers:

```bash
# Method 1: Using main.py
python main.py

# Method 2: Using launch_inspector.py
python launch_inspector.py
```

This will:
- Open a web browser with the MCP inspector
- Connect to the research server for testing
- Allow you to test MCP tools interactively

### Option 2: Multi-Server Chatbot

Run the enhanced chatbot that connects to multiple MCP servers:

```bash
cd mcp_project
source .venv/bin/activate
uv run mcp_chatbot.py
```

The chatbot connects to three MCP servers:
- **Filesystem Server**: File and directory operations
- **Research Server**: Academic paper searches on arXiv
- **Fetch Server**: Web content retrieval

## 🔧 Configuration

### Server Configuration (`mcp_project/server_config.json`)

```json
{
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
        },
        "research": {
            "command": "uv",
            "args": ["run", "research_server.py"]
        },
        "fetch": {
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        }
    }
}
```

## 💬 Example Chatbot Queries

### Web Content + File Operations
```
Fetch the content of https://modelcontextprotocol.io/docs/concepts/architecture 
and save the content in the file "mcp_summary.md"
```

### Research + Web + File Operations
```
Fetch deeplearning.ai and find an interesting term. 
Search for 2 papers around the term and then summarize 
your findings and write them to a file called results.txt
```

### File System Operations
```
List all files in the current directory and create a summary
```

## 🧪 Testing

Test the MCP server inspector:

```bash
# Test the research server
cd mcp_project
uv run research_server.py
```

## 📚 API Reference

### Research Server Tools

- `search_papers(topic: str, max_results: int = 5)`: Search arXiv for papers
- `extract_info(paper_id: str)`: Get detailed information about a specific paper

### Filesystem Server Tools

- File and directory listing, reading, writing operations
- Works within the current directory (`.`)

### Fetch Server Tools

- `fetch(url: str)`: Retrieve web content as markdown

## 🔍 Architecture

### Multi-Server Chatbot Architecture

1. **Multiple Sessions**: Maintains separate client sessions for each MCP server
2. **Tool Mapping**: Maps tool names to their corresponding server sessions
3. **Resource Management**: Uses AsyncExitStack for proper cleanup
4. **Dynamic Loading**: Reads server configurations from JSON file

### Key Components

- **MCP_ChatBot**: Main chatbot class with multi-server support
- **AsyncExitStack**: Manages multiple MCP client connections
- **Tool Routing**: Routes tool calls to appropriate servers
- **Configuration**: JSON-based server configuration

## 🛠️ Development

### Adding New Servers

1. Add server configuration to `server_config.json`
2. The chatbot will automatically connect to new servers
3. Tools will be available immediately

### Customizing Tools

- Modify `research_server.py` to add new research tools
- Create new MCP servers following the MCP protocol
- Update server configuration as needed

## 📝 Requirements

- Python 3.13+
- Node.js (for inspector and filesystem server)
- uv (Python package manager)
- Internet connection (for arXiv searches and web fetching)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 Credits & Acknowledgments

This project is based on the **MCP: Build Rich-Context AI Apps with Anthropic** course from DeepLearning.AI with significant enhancements and improvements.

### Original Tutorial
- **Source**: [MCP: Build Rich-Context AI Apps with Anthropic](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/)
- **Instructor**: Elie Schoppik (Head of Technical Education at Anthropic)
- **Platform**: DeepLearning.AI
- **Framework**: Model Context Protocol (MCP)
- **Base Implementation**: Multi-server MCP chatbot with Anthropic Claude integration

### Enhancements Made
- **🆕 Asynchronous Server Connections**: Replaced sequential server connections with parallel connections using `asyncio.gather()` for faster startup times
- **🆕 Tool Namespacing**: Implemented conflict resolution for tools with the same name across different servers using underscore-separated names (e.g., `filesystem_read_file`)
- **🆕 Improved Error Handling**: Enhanced error handling and logging for better debugging
- **🆕 Better Resource Management**: Optimized AsyncExitStack usage for cleaner resource cleanup

### Technologies Used
- **Python 3.13+**: Core implementation language
- **Anthropic Claude 3.5 Sonnet**: AI model for natural language processing
- **Model Context Protocol (MCP)**: Protocol for AI model tool integration
- **asyncio**: Asynchronous programming for parallel operations
- **Node.js**: Required for MCP inspector and filesystem server

### Learning Outcomes
This project demonstrates:
- Advanced async/await patterns in Python
- Multi-server architecture design
- Tool conflict resolution strategies
- MCP protocol implementation
- AI model integration with external tools

### About the Original Course
The [MCP course from DeepLearning.AI](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/) teaches the core concepts of the Model Context Protocol and how to implement it in AI applications. MCP is an open protocol that standardizes how LLM applications can access context through tools and data resources using a client-server architecture.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
