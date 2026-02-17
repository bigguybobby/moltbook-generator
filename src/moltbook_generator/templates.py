"""
MoltBook Templates

Generate MoltBook output from parsed repository metadata.
Supports multiple output formats: YAML, JSON, and Markdown.
Provides specialised templates for different tool types.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Literal


OutputFormat = Literal["yaml", "json", "markdown"]

TOOL_TYPES = ("cli", "library", "web-app", "service", "plugin", "mcp-server", "github-action")


class MoltBookTemplate:
    """Generate MoltBook listings in multiple formats from parsed metadata.

    Supported output formats:
    - ``yaml`` (default) — YAML document ready for marketplace submission
    - ``json``           — JSON object with identical fields
    - ``markdown``       — Human-readable README-style Markdown card
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(
        self,
        metadata: Dict[str, Any],
        tool_type: str,
        keywords: List[str],
        output_format: OutputFormat = "yaml",
        author: str = "",
        license_id: str = "MIT",
        repository: str = "",
    ) -> str:
        """Render a complete MoltBook listing.

        Args:
            metadata: Parsed repository metadata dict (from :class:`RepoParser`).
            tool_type: Type of tool: one of :data:`TOOL_TYPES`.
            keywords: Extracted keyword list (up to 10 used).
            output_format: ``"yaml"``, ``"json"``, or ``"markdown"``.
            author: Author name or GitHub handle.
            license_id: SPDX license identifier (e.g. ``"MIT"``).
            repository: Repository URL.

        Returns:
            Rendered listing string in the requested format.
        """
        data = self._build_data(metadata, tool_type, keywords, author, license_id, repository)

        if output_format == "json":
            return self._render_json(data)
        elif output_format == "markdown":
            return self._render_markdown(data, metadata, tool_type)
        else:
            return self._render_yaml(data, metadata, tool_type)

    def render_full_listing(
        self,
        metadata: Dict[str, Any],
        tool_type: str,
        keywords: List[str],
        author: str = "",
        license_id: str = "MIT",
        repository: str = "",
        output_format: OutputFormat = "yaml",
    ) -> str:
        """Alias for :meth:`render` kept for backwards compatibility.

        Args:
            metadata: Parsed repository metadata.
            tool_type: Tool type string.
            keywords: Keyword list.
            author: Author name.
            license_id: SPDX license identifier.
            repository: Repository URL.
            output_format: Output format.

        Returns:
            Rendered listing string.
        """
        return self.render(
            metadata=metadata,
            tool_type=tool_type,
            keywords=keywords,
            output_format=output_format,
            author=author,
            license_id=license_id,
            repository=repository,
        )

    # ------------------------------------------------------------------
    # Data assembly
    # ------------------------------------------------------------------

    def _build_data(
        self,
        metadata: Dict[str, Any],
        tool_type: str,
        keywords: List[str],
        author: str,
        license_id: str,
        repository: str,
    ) -> Dict[str, Any]:
        """Assemble a normalised data dict shared by all renderers.

        Args:
            metadata: Raw metadata from parser.
            tool_type: Tool type string.
            keywords: Keyword list.
            author: Author name.
            license_id: SPDX license.
            repository: Repo URL.

        Returns:
            Normalised data dict.
        """
        name = metadata.get("name", "unknown-tool")
        language = metadata.get("language", "Unknown")

        return {
            "name": name,
            "version": metadata.get("version", "0.1.0"),
            "type": tool_type,
            "language": language,
            "keywords": keywords[:10],
            "description": (
                metadata.get("ai_description")
                or metadata.get("description", "")
                or f"A {language} tool."
            ),
            "installation": self._build_installation(metadata, tool_type),
            "usage": self._build_usage(metadata, tool_type),
            "requirements": self._build_requirements(metadata),
            "features": metadata.get("features", [])[:5],
            "author": author or metadata.get("author", "Unknown"),
            "license": license_id,
            "repository": repository or metadata.get("repository", ""),
            "homepage": metadata.get("homepage", ""),
            "status": "active",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # ------------------------------------------------------------------
    # YAML renderer
    # ------------------------------------------------------------------

    def _render_yaml(self, data: Dict[str, Any], metadata: Dict[str, Any], tool_type: str) -> str:
        """Render the listing as YAML.

        Args:
            data: Normalised data dict from :meth:`_build_data`.
            metadata: Raw metadata (for section-level rendering).
            tool_type: Tool type string.

        Returns:
            YAML string.
        """
        keywords_yaml = "\n".join(f"  - {kw}" for kw in data["keywords"]) or "  []"
        features_yaml = (
            "\n".join(f"  - {f}" for f in data["features"])
            if data["features"]
            else "  []"
        )

        desc = data["description"].replace('"', '\\"')
        # Multi-line description
        if "\n" in desc:
            desc_block = "|\n  " + desc.replace("\n", "\n  ")
            desc_yaml = f"description: {desc_block}"
        else:
            desc_yaml = f'description: "{desc}"'

        lines = [
            f"# MoltBook Listing",
            f"# Generated: {data['generated_at']}",
            f"# Tool: {data['name']}",
            "",
            f"name: {data['name']}",
            f"version: {data['version']}",
            f"type: {data['type']}",
            f"language: {data['language']}",
            f"author: {data['author']}",
            f"license: {data['license']}",
            f"status: {data['status']}",
            f"last_updated: {data['last_updated']}",
            "",
            f"keywords:",
            keywords_yaml,
            "",
            desc_yaml,
            "",
            f"features:",
            features_yaml,
            "",
            f'installation: "{data["installation"]}"',
            f'usage: "{data["usage"]}"',
            f'requirements: "{data["requirements"]}"',
        ]

        if data["repository"]:
            lines.append(f'repository: "{data["repository"]}"')
        if data["homepage"]:
            lines.append(f'homepage: "{data["homepage"]}"')

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # JSON renderer
    # ------------------------------------------------------------------

    def _render_json(self, data: Dict[str, Any]) -> str:
        """Render the listing as formatted JSON.

        Args:
            data: Normalised data dict.

        Returns:
            JSON string (pretty-printed).
        """
        # Remove internal-only key before serialising
        output = {k: v for k, v in data.items() if k != "generated_at"}
        output["generated_at"] = data["generated_at"]
        return json.dumps(output, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Markdown renderer
    # ------------------------------------------------------------------

    def _render_markdown(
        self, data: Dict[str, Any], metadata: Dict[str, Any], tool_type: str
    ) -> str:
        """Render the listing as a Markdown card (README-style).

        Args:
            data: Normalised data dict.
            metadata: Raw metadata for extras.
            tool_type: Tool type string.

        Returns:
            Markdown string.
        """
        kw_badges = " ".join(
            f"`{kw}`" for kw in data["keywords"]
        )
        features_md = (
            "\n".join(f"- {f}" for f in data["features"])
            if data["features"]
            else "_No features listed._"
        )

        install_cmd = data["installation"]
        usage_cmd = data["usage"]
        lang = data["language"]

        lines = [
            f"# {data['name']} `v{data['version']}`",
            "",
            f"> {data['description']}",
            "",
            f"**Type:** {data['type']} &nbsp;|&nbsp; "
            f"**Language:** {lang} &nbsp;|&nbsp; "
            f"**License:** {data['license']}",
            "",
            f"**Keywords:** {kw_badges}",
            "",
            "---",
            "",
            "## Installation",
            "",
            f"```{self._lang_to_fence(lang)}",
            install_cmd,
            "```",
            "",
            "## Usage",
            "",
            f"```{self._lang_to_fence(lang)}",
            usage_cmd,
            "```",
            "",
            "## Features",
            "",
            features_md,
            "",
            "## Requirements",
            "",
            f"- {data['requirements']}",
            "",
            "---",
            "",
            f"**Author:** {data['author']}  ",
            f"**Repository:** {data['repository'] or '_not set_'}  ",
            f"**Last updated:** {data['last_updated']}  ",
            f"**Generated:** {data['generated_at']}",
        ]

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lang_to_fence(language: str) -> str:
        """Map language name to Markdown fenced-code tag.

        Args:
            language: Language name from metadata.

        Returns:
            Markdown code fence language identifier.
        """
        mapping = {
            "python": "bash",
            "javascript": "bash",
            "typescript": "bash",
            "rust": "bash",
            "go": "bash",
        }
        return mapping.get(language.lower(), "bash")

    @staticmethod
    def _build_installation(metadata: Dict[str, Any], tool_type: str) -> str:
        """Build an install command appropriate for the tool's language.

        Args:
            metadata: Repository metadata.
            tool_type: Detected tool type.

        Returns:
            Install command string.
        """
        lang = metadata.get("language", "").lower()
        name = metadata.get("name", "unknown-tool")

        if tool_type == "github-action":
            return f"uses: {metadata.get('repository', 'owner/repo')}@v1"

        if "python" in lang:
            return f"pip install {name}"
        elif "javascript" in lang or "typescript" in lang:
            if tool_type == "cli":
                return f"npm install -g {name}"
            return f"npm install {name}"
        elif "rust" in lang:
            return f"cargo install {name}"
        elif "go" in lang:
            return f"go install github.com/{name}@latest"
        return "# See documentation for installation instructions"

    @staticmethod
    def _build_usage(metadata: Dict[str, Any], tool_type: str) -> str:
        """Build a minimal usage example string.

        Args:
            metadata: Repository metadata.
            tool_type: Detected tool type.

        Returns:
            Usage example string.
        """
        lang = metadata.get("language", "").lower()
        name = metadata.get("name", "tool")

        if tool_type in ("cli", "mcp-server"):
            if cmds := metadata.get("cli_commands"):
                return f"{cmds[0]} --help"
            return f"{name} --help"

        if tool_type == "github-action":
            return f"- uses: {name}@v1\n  with:\n    api-key: ${{{{ secrets.API_KEY }}}}"

        if tool_type == "library":
            if "python" in lang:
                return f"from {name.replace('-', '_')} import {name.replace('-', '_').title()}"
            elif "javascript" in lang or "typescript" in lang:
                return f"import {{ {name} }} from '{name}';"
            elif "rust" in lang:
                return f"use {name.replace('-', '_')}::*;"

        return "# See documentation for usage examples"

    @staticmethod
    def _build_requirements(metadata: Dict[str, Any]) -> str:
        """Return a human-readable minimum requirement string.

        Args:
            metadata: Repository metadata.

        Returns:
            Requirements string.
        """
        lang = metadata.get("language", "").lower()

        requirements = {
            "python": "Python >= 3.9",
            "javascript": "Node.js >= 18",
            "typescript": "Node.js >= 18",
            "rust": "Rust >= 1.70",
            "go": "Go >= 1.21",
        }
        return requirements.get(lang, "See repository for requirements")
