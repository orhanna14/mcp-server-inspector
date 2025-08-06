from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List, Dict, TypedDict
from contextlib import AsyncExitStack
import json
import asyncio

load_dotenv()

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.sessions: List[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.available_tools: List[ToolDefinition] = []
        self.tool_to_session: Dict[str, ClientSession] = {}

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions.append(session)
            
            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
            
            for tool in tools:
                # Namespace the tool name with the server name using underscore
                namespaced_tool_name = f"{server_name}_{tool.name}"
                
                # Check for conflicts
                if tool.name in self.tool_to_session:
                    print(f"Warning: Tool '{tool.name}' exists in multiple servers. Using namespaced version: '{namespaced_tool_name}'")
                
                self.tool_to_session[namespaced_tool_name] = session
                self.available_tools.append({
                    "name": namespaced_tool_name,
                    "description": f"[{server_name}] {tool.description}",
                    "input_schema": tool.inputSchema
                })
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")

    async def connect_to_servers(self):
        """Connect to all configured MCP servers asynchronously."""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            # Create tasks for all server connections
            tasks = [
                self.connect_to_server(server_name, server_config)
                for server_name, server_config in servers.items()
            ]
            
            # Connect to all servers in parallel
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        response = self.anthropic.messages.create(max_tokens = 2024,
                                      model = 'claude-3-7-sonnet-20250219', 
                                      tools = self.available_tools,
                                      messages = messages)
        process_query = True
        while process_query:
            assistant_content = []
            for content in response.content:
                if content.type =='text':
                    print(content.text)
                    assistant_content.append(content)
                    if(len(response.content) == 1):
                        process_query= False
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    messages.append({'role':'assistant', 'content':assistant_content})
                    tool_id = content.id
                    tool_args = content.input
                    tool_name = content.name
                    
    
                    print(f"Calling tool {tool_name} with args {tool_args}")
                    
                    # Call a tool - now using namespaced tool names
                    if tool_name in self.tool_to_session:
                        session = self.tool_to_session[tool_name]
                        # Extract the original tool name (without namespace) for the actual call
                        original_tool_name = tool_name.split('_', 1)[1] if '_' in tool_name else tool_name
                        result = await session.call_tool(original_tool_name, arguments=tool_args)
                    else:
                        # Fallback: try to find the tool without namespace
                        original_tool_name = tool_name.split('_', 1)[1] if '_' in tool_name else tool_name
                        session = None
                        for namespaced_name, sess in self.tool_to_session.items():
                            if namespaced_name.endswith(f".{original_tool_name}"):
                                session = sess
                                break
                        
                        if session:
                            result = await session.call_tool(original_tool_name, arguments=tool_args)
                        else:
                            raise ValueError(f"Tool '{tool_name}' not found")
                    
                    messages.append({"role": "user", 
                                      "content": [
                                          {
                                              "type": "tool_result",
                                              "tool_use_id":tool_id,
                                              "content": result.content
                                          }
                                      ]
                                    })
                    response = self.anthropic.messages.create(max_tokens = 2024,
                                      model = 'claude-3-7-sonnet-20250219', 
                                      tools = self.available_tools,
                                      messages = messages) 
                    
                    if(len(response.content) == 1 and response.content[0].type == "text"):
                        print(response.content[0].text)
                        process_query= False

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Cleanly close all resources using AsyncExitStack."""
        try:
            await self.exit_stack.aclose()
        except RuntimeError as e:
            if "cancel scope" in str(e):
                # Handle the cancel scope error gracefully
                print("Cleaning up resources...")
            else:
                raise

async def main():
    chatbot = MCP_ChatBot()
    try:
        # the mcp clients and sessions are not initialized using "with"
        # like in the previous lesson
        # so the cleanup should be manually handled
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        try:
            await chatbot.cleanup()
        except Exception as e:
            print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 