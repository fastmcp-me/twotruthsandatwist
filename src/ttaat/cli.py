#!/usr/bin/env python3
import argparse
import sys
from .version import TTAAT_VERSION
from .db import initialize_db, ensure_db_path


def handle_db_upgrade(args):
    """Initialize or upgrade the database."""
    from .db import upgrade_db
    
    db_path = ensure_db_path()
    print(f"Database path: {db_path}")
    
    # Upgrade the database (creates it if it doesn't exist)
    try:
        was_upgraded, old_version, new_version = upgrade_db()
        
        if was_upgraded:
            if old_version is None:
                print("Database initialized successfully.")
            else:
                print(f"Database upgraded from version {old_version} to {new_version}.")
        else:
            print(f"Database is already at the latest version ({new_version}).")
    except Exception as e:
        print(f"Error upgrading database: {e}")


def handle_db_stats(args):
    """Show database statistics."""
    from .db import get_total_rounds, get_score, get_twist_index_stats
    
    db_path = ensure_db_path()
    print(f"Database path: {db_path}")
    
    try:
        # Gather statistics
        total_rounds = get_total_rounds()
        player_score, gm_score = get_score()
        twist_stats = get_twist_index_stats()
        
        # Display statistics
        print(f"\nGame Statistics:")
        print(f"---------------")
        print(f"Total rounds played: {total_rounds}")
        print(f"Player score: {player_score}")
        print(f"Game master score: {gm_score}")
        
        # Convert index numbers to more meaningful labels
        index_labels = {0: "First statement", 1: "Second statement", 2: "Third statement"}
        
        print(f"\nTwist distribution:")
        for index, count in twist_stats.items():
            percentage = (count / total_rounds * 100) if total_rounds > 0 else 0
            print(f"  {index_labels[index]}: {count} times ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        print("Make sure the database is initialized with 'ttaat db upgrade'")


def handle_serve(args):
    """Start the MCP server."""
    # Don't print anything to stdout as it will interfere with the MCP protocol
    # Instead, use stderr for logging
    import sys
    print("Starting Two Truths and a Twist MCP server...", file=sys.stderr)
    
    # Import here to avoid circular imports
    from .mcp import serve_mcp
    serve_mcp()


def generate_argument_parser():
    parser = argparse.ArgumentParser(description="Two Truths and a Twist CLI")
    parser.add_argument('-v', '--version', action='version', version=TTAAT_VERSION)
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command')
    
    # Database commands
    db_parser = subparsers.add_parser('db', help='Database commands')
    db_subparsers = db_parser.add_subparsers(dest='db_command')
    
    # db upgrade command
    upgrade_parser = db_subparsers.add_parser('upgrade', help='Initialize or upgrade the database')
    upgrade_parser.set_defaults(func=handle_db_upgrade)
    
    # db stats command
    stats_parser = db_subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.set_defaults(func=handle_db_stats)
    
    # serve command
    serve_parser = subparsers.add_parser('serve', help='Start the MCP server')
    serve_parser.set_defaults(func=handle_serve)
    
    parser.set_defaults(func=lambda _: parser.print_help())
    
    return parser


def main() -> None:
    import sys
    
    # Special handling for 'serve' command to prevent stdout pollution
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        # Import and call serve_mcp directly, bypassing argparse
        from .mcp import serve_mcp
        print("Starting Two Truths and a Twist MCP server...", file=sys.stderr)
        serve_mcp()
    else:
        # Normal CLI operation
        parser = generate_argument_parser()
        args = parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    main()