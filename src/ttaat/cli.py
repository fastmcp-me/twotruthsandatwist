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
    # Import here to avoid circular imports
    from .mcp import serve_mcp
    
    # stdout should already be redirected to stderr in main()
    # so we don't need additional redirection here
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
    # Redirect stdout to stderr for the entire process when using MCP
    # This ensures argparse help messages don't interfere with the protocol
    import sys
    
    # Parse arguments normally
    parser = generate_argument_parser()
    args = parser.parse_args()
    
    # Only redirect stdout for the serve command
    if hasattr(args, 'command') and args.command == 'serve':
        # This redirects stdout to stderr, ensuring clean stdout for MCP
        sys.stdout = sys.stderr
        print("Starting Two Truths and a Twist MCP server...", file=sys.stderr)
    
    # Execute the command
    args.func(args)


if __name__ == "__main__":
    main()