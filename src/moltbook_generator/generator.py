"""
MoltBook Generator Core

Core logic for parsing repositories, extracting metadata,
and generating MoltBook listings with AI-enhanced descriptions.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from .parsers import RepoParser
from .templates import MoltBookTemplate


class MoltBookGenerator:
    """Main generator class for creating MoltBook listings."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        verbose: bool = False,
        use_ai: bool = True,
    ):
        """
        Initialize the generator.

        Args:
            api_key: Anthropic API key for AI features
            verbose: Enable verbose logging
            use_ai: Whether to use AI for description generation
        """
        self.api_key = api_key
        self.verbose = verbose
        self.use_ai = use_ai and api_key and Anthropic

        if self.use_ai:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None

        self.parser = RepoParser()
        self.template = MoltBookTemplate()

    def generate(
        self,
        source: str,
        tool_type: Optional[str] = None,
        output_format: str = "yaml",
    ) -> str:
        """
        Generate a MoltBook listing from a source.

        Args:
            source: GitHub URL or local directory path
            tool_type: Override tool type detection
            output_format: Output format: 'yaml', 'json', or 'markdown'

        Returns:
            Listing as string in the requested format
        """
        # Determine if source is URL or local path
        is_url = source.startswith("http://") or source.startswith("https://")

        if is_url:
            repo_path = self._clone_repo(source)
            cleanup = True
        else:
            repo_path = Path(source).resolve()
            cleanup = False
            if not repo_path.exists():
                raise ValueError(f"Directory not found: {repo_path}")

        try:
            # Parse repository
            if self.verbose:
                print(f"Parsing repository: {repo_path}")

            metadata = self.parser.parse(repo_path)

            # Auto-detect tool type if not specified
            if tool_type is None:
                tool_type = self._detect_tool_type(metadata)

            if self.verbose:
                print(f"Detected tool type: {tool_type}")

            # Enhance description with AI
            if self.use_ai:
                if self.verbose:
                    print("Generating AI-enhanced description...")
                metadata["ai_description"] = self._generate_ai_description(
                    metadata
                )

            # Extract keywords
            keywords = self._extract_keywords(metadata)

            if self.verbose:
                print(f"Extracted keywords: {', '.join(keywords)}")

            # Generate MoltBook listing in requested format
            listing = self.template.render(
                metadata=metadata,
                tool_type=tool_type,
                keywords=keywords,
                output_format=output_format,
            )

            return listing

        finally:
            # Cleanup temporary clone
            if cleanup and repo_path.exists():
                shutil.rmtree(repo_path, ignore_errors=True)

    def _clone_repo(self, url: str) -> Path:
        """Clone a GitHub repository to a temporary directory."""
        try:
            import git
        except ImportError:
            raise ImportError(
                "GitPython is required for cloning repositories. "
                "Install it with: pip install gitpython"
            )

        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="moltbook_"))

        if self.verbose:
            print(f"Cloning {url} to {temp_dir}")

        try:
            # Clone with depth=1 for speed
            git.Repo.clone_from(url, temp_dir, depth=1)
            return temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {e}")

    def _detect_tool_type(self, metadata: Dict[str, Any]) -> str:
        """Auto-detect the tool type from metadata."""
        # Check for CLI indicators
        if metadata.get("has_bin") or metadata.get("cli_commands"):
            return "cli"

        # Check for web app indicators
        if metadata.get("has_web_framework"):
            return "web-app"

        # Check for service indicators
        if metadata.get("has_server") or metadata.get("has_daemon"):
            return "service"

        # Check for plugin indicators
        if "plugin" in metadata.get("name", "").lower():
            return "plugin"

        # Default to library
        return "library"

    def _generate_ai_description(self, metadata: Dict[str, Any]) -> str:
        """Generate an optimized description using Claude."""
        if not self.client:
            return metadata.get("description", "")

        # Build context prompt
        context = f"""
Repository: {metadata.get('name', 'Unknown')}
Description: {metadata.get('description', 'No description')}
README excerpt: {metadata.get('readme_excerpt', 'No README')}
Language: {metadata.get('language', 'Unknown')}
Features: {', '.join(metadata.get('features', []))}
"""

        prompt = f"""
Given this repository information, generate a concise, compelling MoltBook listing description.

{context}

Requirements:
- 1-2 sentences maximum
- Focus on what the tool does and its key benefit
- Use active voice
- Be specific and concrete
- Avoid marketing fluff
- Target developers as the audience

Generate only the description, no preamble:
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text.strip()

        except Exception as e:
            if self.verbose:
                print(f"AI generation failed: {e}")
            return metadata.get("description", "")

    def _extract_keywords(self, metadata: Dict[str, Any]) -> list:
        """Extract relevant keywords from metadata."""
        keywords = set()

        # Add language/ecosystem
        if lang := metadata.get("language"):
            keywords.add(lang.lower())

        # Add framework/library names
        for dep in metadata.get("dependencies", []):
            # Extract base package name
            base = dep.split("/")[-1].split("@")[0].split("==")[0]
            if len(base) > 2:  # Skip very short names
                keywords.add(base.lower())

        # Add from description/readme
        text = (
            f"{metadata.get('description', '')} "
            f"{metadata.get('readme_excerpt', '')}"
        )

        common_keywords = {
            "cli", "api", "web", "database", "testing", "automation",
            "monitoring", "deployment", "security", "parser", "generator",
            "framework", "library", "tool", "utility", "service",
        }

        for word in text.lower().split():
            word = word.strip(".,;:!?")
            if word in common_keywords:
                keywords.add(word)

        # Limit to top 10 most relevant
        return sorted(list(keywords))[:10]
