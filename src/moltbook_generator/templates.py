"""
MoltBook Templates

Generate MoltBook YAML format from parsed metadata.
Provides templates for different tool types.
"""

from typing import Dict, Any, List
from datetime import datetime


class MoltBookTemplate:
    """Generate MoltBook listing YAML from metadata."""

    def render(
        self,
        metadata: Dict[str, Any],
        tool_type: str,
        keywords: List[str],
    ) -> str:
        """
        Render a complete MoltBook listing.

        Args:
            metadata: Parsed repository metadata
            tool_type: Type of tool (cli, library, web-app, etc.)
            keywords: Extracted keywords

        Returns:
            YAML-formatted MoltBook listing
        """
        sections = [
            self._render_header(metadata),
            self._render_metadata(metadata, tool_type, keywords),
            self._render_description(metadata),
            self._render_features(metadata),
            self._render_installation(metadata, tool_type),
            self._render_usage(metadata, tool_type),
            self._render_requirements(metadata),
        ]

        return "\n".join(s for s in sections if s)

    def _render_header(self, metadata: Dict[str, Any]) -> str:
        """Render YAML header."""
        return f"""# MoltBook Listing
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Tool: {metadata.get('name', 'Unknown')}
"""

    def _render_metadata(
        self, metadata: Dict[str, Any], tool_type: str, keywords: List[str]
    ) -> str:
        """Render metadata section."""
        name = metadata.get("name", "unknown-tool")
        version = metadata.get("version", "0.1.0")
        language = metadata.get("language", "Unknown")

        keywords_yaml = "\n".join(f"  - {kw}" for kw in keywords[:10])

        return f"""name: {name}
version: {version}
type: {tool_type}
language: {language}
keywords:
{keywords_yaml}"""

    def _render_description(self, metadata: Dict[str, Any]) -> str:
        """Render description section."""
        # Prefer AI-generated description
        desc = metadata.get("ai_description") or metadata.get("description", "")

        if not desc:
            desc = f"A {metadata.get('language', 'software')} tool for developers."

        # Ensure proper YAML formatting for multiline
        desc_lines = desc.split("\n")
        if len(desc_lines) == 1:
            return f'\ndescription: "{desc}"'
        else:
            formatted = "\n  ".join(desc_lines)
            return f'\ndescription: |\n  {formatted}'

    def _render_features(self, metadata: Dict[str, Any]) -> str:
        """Render features section."""
        features = metadata.get("features", [])

        if not features:
            return ""

        features_yaml = "\n".join(f"  - {feat}" for feat in features[:5])
        return f"\nfeatures:\n{features_yaml}"

    def _render_installation(self, metadata: Dict[str, Any], tool_type: str) -> str:
        """Render installation instructions."""
        language = metadata.get("language", "").lower()
        name = metadata.get("name", "unknown-tool")

        if "python" in language:
            install = f"pip install {name}"
        elif "javascript" in language or "typescript" in language:
            install = f"npm install -g {name}"
        elif "rust" in language:
            install = f"cargo install {name}"
        elif "go" in language:
            install = f"go install {name}@latest"
        else:
            install = f"# See documentation for installation instructions"

        return f'\ninstallation: "{install}"'

    def _render_usage(self, metadata: Dict[str, Any], tool_type: str) -> str:
        """Render basic usage example."""
        if tool_type == "cli":
            if commands := metadata.get("cli_commands"):
                cmd = commands[0]
                return f'\nusage: "{cmd} --help"'
            else:
                name = metadata.get("name", "tool")
                return f'\nusage: "{name} --help"'

        elif tool_type == "library":
            language = metadata.get("language", "").lower()
            name = metadata.get("name", "unknown")

            if "python" in language:
                return f'\nusage: "import {name.replace("-", "_")}"'
            elif "javascript" in language or "typescript" in language:
                return f'\nusage: "import {{ {name} }} from \'{name}\';"'
            elif "rust" in language:
                return f'\nusage: "use {name};"'

        return '\nusage: "See documentation for usage examples"'

    def _render_requirements(self, metadata: Dict[str, Any]) -> str:
        """Render requirements/dependencies section."""
        language = metadata.get("language", "").lower()

        if "python" in language:
            req = "Python >= 3.9"
        elif "javascript" in language or "typescript" in language:
            req = "Node.js >= 18"
        elif "rust" in language:
            req = "Rust >= 1.70"
        elif "go" in language:
            req = "Go >= 1.20"
        else:
            return ""

        return f'\nrequirements: "{req}"'

    def render_full_listing(
        self,
        metadata: Dict[str, Any],
        tool_type: str,
        keywords: List[str],
        author: str = "",
        license: str = "MIT",
        repository: str = "",
    ) -> str:
        """
        Render a complete, production-ready MoltBook listing.

        Includes all optional fields for maximum compatibility.
        """
        base = self.render(metadata, tool_type, keywords)

        additional = f"""
author: {author or "Unknown"}
license: {license}
repository: {repository}
status: active
last_updated: {datetime.now().strftime("%Y-%m-%d")}
"""

        return base + additional
