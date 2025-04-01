#!/usr/bin/env python3
import argparse
import sys
from .version import TTAAT_VERSION


def generate_argument_parser():
    parser = argparse.ArgumentParser(description="Two Truths and a Twist CLI")
    parser.add_argument('-v', '--version', action='version', version=TTAAT_VERSION)
    
    parser.set_defaults(func=lambda _: parser.print_help())
    
    return parser


def main() -> None:
    parser = generate_argument_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()