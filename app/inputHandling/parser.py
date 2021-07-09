import argparse
import json

def parser() -> argparse.ArgumentParser:
    """
    Returns the argument parser for this tool.

    """
    parser = argparse.ArgumentParser(description='Generate cost table for specificed aws accounts.')

    parser.add_argument(
                    '--token',
                    help='Authentication token'
                        )
    parser.add_argument(
                    '--months',
                    default=6,
                    type=int,
                    help='Number of months ago to start report from.'
                    )
    parser.add_argument(
                    '--accounts',
                    default='[]',
                    help='JSON array of objects containing all account data',
                    )
    return parser
