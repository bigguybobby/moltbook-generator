#!/usr/bin/env python3
"""
MoltBook Generator CLI

Command-line interface for generating MoltBook listings from GitHub repositories.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .generator import MoltBookGenerator
from . import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate MoltBook listings from GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from GitHub URL
  moltbook-gen https://github.com/user/repo

  # Generate from local directory
  moltbook-gen ./my-project

  # Preview without saving
  moltbook-gen https://github.com/user/repo --preview

  # Specify output file
  moltbook-gen https://github.com/user/repo -o listing.yaml

  # Skip AI enhancement
  moltbook-gen https://github.com/user/repo --no-ai
        """,
    )

    parser.add_argument("source", help="GitHub URL or local directory path")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path (default: <repo-name>-moltbook.yaml)",
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview output without saving to file",
    )

    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI-powered description generation",
    )

    parser.add_argument(
        "--tool-type",
        type=str,
        choices=["cli", "library", "web-app", "service", "plugin", "auto"],
        default="auto",
        help="Tool type (default: auto-detect)",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )

    parser.add_argument(
        "--version", action="version", version=f"moltbook-generator {__version__}"
    )

    args = parser.parse_args()

    # Handle API key
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not args.no_ai and not api_key:
        print(
            "Warning: No Anthropic API key provided. Using --no-ai mode.",
            file=sys.stderr,
        )
        args.no_ai = True

    try:
        # Initialize generator
        generator = MoltBookGenerator(
            api_key=api_key,
            verbose=args.verbose,
            use_ai=not args.no_ai,
        )

        # Generate listing
        if args.verbose:
            print(f"Processing: {args.source}")

        listing = generator.generate(
            source=args.source,
            tool_type=args.tool_type if args.tool_type != "auto" else None,
        )

        # Preview mode
        if args.preview:
            print("\n" + "=" * 60)
            print("PREVIEW")
            print("=" * 60)
            print(listing)
            return 0

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Extract repo name from source
            if args.source.startswith("http"):
                repo_name = args.source.rstrip("/").split("/")[-1]
                repo_name = repo_name.replace(".git", "")
            else:
                repo_name = Path(args.source).resolve().name

            output_path = Path(f"{repo_name}-moltbook.yaml")

        # Write output
        output_path.write_text(listing)
        print(f"✓ Generated: {output_path}")

        if args.verbose:
            print(f"\nOutput size: {len(listing)} bytes")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
