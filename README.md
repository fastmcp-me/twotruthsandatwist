# TwoTruthsAndATwist

Two Truths and a Twist: The world's first Model Context Protocol (MCP) game

## Installation

### Requirements
- Python 3.13 or higher
- MCP-compatible LLM (like Claude 3)

You can install the game directly from PyPI:

```bash
pip install ttaat
```

Or if you prefer using `uv`:

```bash
uv pip install ttaat
```

## Usage

### Initialize the Database
First, initialize the game database:

```bash
ttaat db upgrade
```

### Start the Game Server
To start the MCP server:

```bash
ttaat serve
```

This will start the Two Truths and a Twist MCP server on port 8000, which LLMs can connect to for playing the game.

### View Game Statistics
To see game statistics:

```bash
ttaat db stats
```

## Game Mechanics

Two Truths and a Twist is a trivia game where:

1. The AI creates a round with three statements about a topic - two truths and one "twist" (a playful, false statement)
2. Players try to identify which statement is the twist 
3. The AI reveals the answer with entertaining explanations

The game leverages the MCP protocol to provide a fun, interactive trivia experience where AI models both generate the content and facilitate gameplay.

## For Developers

This package implements an MCP server that provides custom game tools:
- `create_round`: Creates a new game round with a question and three statements
- `submit_guess`: Lets players submit their guess for which statement is the twist
- `reveal_twist`: Reveals the answer with explanations for each statement
- `get_round`: Retrieves details for a specific round
- `get_last_round`: Gets details of the most recent round
- `get_stats`: Retrieves game statistics

[Detailed game design document](https://docs.google.com/document/d/1kW88UU5bjszQJgyB_JNkpvbnfaSNcKIP4mRR3R-HL1o/edit?usp=sharing)
