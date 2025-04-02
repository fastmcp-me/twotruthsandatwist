#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from contextlib import closing
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types
from pydantic import AnyUrl

from .db import (
    create_round,
    get_last_round,
    get_round,
    submit_guess,
    reveal_twist,
    get_total_rounds,
    get_score,
    get_twist_index_stats,
    upgrade_db,
)

# reconfigure UnicodeEncodeError prone default (i.e. windows-1252) to utf-8
if sys.platform == "win32" and os.environ.get('PYTHONIOENCODING') is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger('ttaat_mcp_server')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TtaatGameServer:
    def __init__(self):
        """Initialize the TTAAT game server."""
        # First, make sure the database is initialized
        was_upgraded, _, _ = upgrade_db()
        if was_upgraded:
            logger.info("Database was upgraded to the latest version")
        else:
            logger.info("Database is already at the latest version")

    async def start_server(self):
        """Start the MCP server for TTAAT."""
        logger.info("Starting Two Truths and a Twist MCP Server")
        
        server = Server("ttaat-game")

        # Register handlers
        logger.debug("Registering handlers")

        @server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools for the TTAAT game."""
            return [
                types.Tool(
                    name="create_round",
                    description="Create a new game round with a question and three statements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "The category of the question"},
                            "question": {"type": "string", "description": "The main question for the round"},
                            "trivia_1": {"type": "string", "description": "First statement"},
                            "trivia_2": {"type": "string", "description": "Second statement"},
                            "trivia_3": {"type": "string", "description": "Third statement"},
                        },
                        "required": ["category", "question", "trivia_1", "trivia_2", "trivia_3"],
                    },
                ),
                types.Tool(
                    name="submit_guess",
                    description="Submit a player's guess for which statement is the twist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "round_id": {"type": "integer", "description": "The ID of the round"},
                            "guess_index": {"type": "integer", "description": "Index of the guessed statement (0, 1, or 2)"},
                        },
                        "required": ["round_id", "guess_index"],
                    },
                ),
                types.Tool(
                    name="reveal_twist",
                    description="Reveal which statement was the twist and provide explanations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "round_id": {"type": "integer", "description": "The ID of the round"},
                            "twist_index": {"type": "integer", "description": "Index of the twist statement (0, 1, or 2)"},
                            "explanation_1": {"type": "string", "description": "Explanation for statement 1"},
                            "explanation_2": {"type": "string", "description": "Explanation for statement 2"},
                            "explanation_3": {"type": "string", "description": "Explanation for statement 3"},
                        },
                        "required": ["round_id", "twist_index", "explanation_1", "explanation_2", "explanation_3"],
                    },
                ),
                types.Tool(
                    name="get_round",
                    description="Get details of a specific round",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "round_id": {"type": "integer", "description": "The ID of the round to retrieve"},
                        },
                        "required": ["round_id"],
                    },
                ),
                types.Tool(
                    name="get_last_round",
                    description="Get details of the most recent round",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="get_stats",
                    description="Get game statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool execution requests."""
            try:
                if name == "create_round":
                    if not arguments:
                        raise ValueError("Missing arguments")
                    
                    required_args = ["category", "question", "trivia_1", "trivia_2", "trivia_3"]
                    for arg in required_args:
                        if arg not in arguments:
                            raise ValueError(f"Missing required argument: {arg}")
                    
                    round_id = create_round(
                        arguments["category"],
                        arguments["question"],
                        arguments["trivia_1"],
                        arguments["trivia_2"],
                        arguments["trivia_3"]
                    )
                    
                    return [types.TextContent(
                        type="text", 
                        text=f"Round created successfully with ID: {round_id}"
                    )]
                
                elif name == "submit_guess":
                    if not arguments or "round_id" not in arguments or "guess_index" not in arguments:
                        raise ValueError("Missing required arguments: round_id and guess_index")
                    
                    round_id = arguments["round_id"]
                    guess_index = arguments["guess_index"]
                    
                    if not isinstance(guess_index, int) or guess_index not in [0, 1, 2]:
                        raise ValueError("guess_index must be 0, 1, or 2")
                    
                    submit_guess(round_id, guess_index)
                    
                    return [types.TextContent(
                        type="text", 
                        text=f"Guess submitted for round {round_id}: statement #{guess_index + 1}"
                    )]
                
                elif name == "reveal_twist":
                    if not arguments:
                        raise ValueError("Missing arguments")
                    
                    required_args = ["round_id", "twist_index", "explanation_1", "explanation_2", "explanation_3"]
                    for arg in required_args:
                        if arg not in arguments:
                            raise ValueError(f"Missing required argument: {arg}")
                    
                    round_id = arguments["round_id"]
                    twist_index = arguments["twist_index"]
                    
                    if not isinstance(twist_index, int) or twist_index not in [0, 1, 2]:
                        raise ValueError("twist_index must be 0, 1, or 2")
                    
                    reveal_twist(
                        round_id,
                        twist_index,
                        arguments["explanation_1"],
                        arguments["explanation_2"],
                        arguments["explanation_3"]
                    )
                    
                    return [types.TextContent(
                        type="text", 
                        text=f"Twist revealed for round {round_id}: statement #{twist_index + 1}"
                    )]
                
                elif name == "get_round":
                    if not arguments or "round_id" not in arguments:
                        raise ValueError("Missing required argument: round_id")
                    
                    round_id = arguments["round_id"]
                    round_data = get_round(round_id)
                    
                    if not round_data:
                        return [types.TextContent(
                            type="text", 
                            text=f"No round found with ID: {round_id}"
                        )]
                    
                    return [types.TextContent(
                        type="text", 
                        text=str(round_data)
                    )]
                
                elif name == "get_last_round":
                    round_data = get_last_round()
                    
                    if not round_data:
                        return [types.TextContent(
                            type="text", 
                            text="No rounds found"
                        )]
                    
                    return [types.TextContent(
                        type="text", 
                        text=str(round_data)
                    )]
                
                elif name == "get_stats":
                    total_rounds = get_total_rounds()
                    player_score, gm_score = get_score()
                    twist_stats = get_twist_index_stats()
                    
                    stats = {
                        "total_rounds": total_rounds,
                        "player_score": player_score,
                        "gm_score": gm_score,
                        "twist_distribution": twist_stats
                    }
                    
                    return [types.TextContent(
                        type="text", 
                        text=str(stats)
                    )]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
            except Exception as e:
                return [types.TextContent(
                    type="text", 
                    text=f"Error: {str(e)}",
                    isError=True
                )]

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Server running with stdio transport")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ttaat",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def serve_mcp():
    """Start the TTAAT MCP server."""
    # Initialize and start the server
    game_server = TtaatGameServer()
    asyncio.run(game_server.start_server())


if __name__ == "__main__":
    serve_mcp()