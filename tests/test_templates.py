"""Tests for MoltBook template rendering."""

from __future__ import annotations

import json
import re

import pytest

from moltbook_generator.templates import MoltBookTemplate, TOOL_TYPES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

METADATA = {
    "name": "my-python-tool",
    "version": "1.2.3",
    "language": "Python",
    "description": "A handy Python utility for developers.",
    "features": ["Fast parsing", "Async support", "Type-safe"],
    "keywords": ["python", "utility"],
    "author": "Alice",
    "homepage": "https://example.com",
    "repository": "https://github.com/alice/my-python-tool",
}

KEYWORDS = ["python", "utility", "cli", "automation"]


@pytest.fixture
def tmpl():
    return MoltBookTemplate()


# ---------------------------------------------------------------------------
# YAML output
# ---------------------------------------------------------------------------

class TestYAMLOutput:
    def test_contains_name(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert "my-python-tool" in output

    def test_contains_version(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert "1.2.3" in output

    def test_contains_type(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="yaml")
        assert "type: library" in output

    def test_contains_all_keywords(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        for kw in KEYWORDS:
            assert kw in output

    def test_keywords_capped_at_10(self, tmpl):
        many_kw = [f"kw{i}" for i in range(20)]
        output = tmpl.render(METADATA, "cli", many_kw, output_format="yaml")
        # Only first 10 should appear
        for kw in many_kw[:10]:
            assert kw in output

    def test_description_included(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert "handy Python utility" in output

    def test_features_included(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert "Fast parsing" in output

    def test_install_command_python(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert "pip install" in output

    def test_starts_with_yaml_comment(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="yaml")
        assert output.startswith("# MoltBook Listing")


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

class TestJSONOutput:
    def test_valid_json(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="json")
        data = json.loads(output)  # must not raise
        assert isinstance(data, dict)

    def test_name_field(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert data["name"] == "my-python-tool"

    def test_version_field(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert data["version"] == "1.2.3"

    def test_keywords_list(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert isinstance(data["keywords"], list)
        assert "python" in data["keywords"]

    def test_type_field(self, tmpl):
        output = tmpl.render(METADATA, "web-app", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert data["type"] == "web-app"

    def test_generated_at_present(self, tmpl):
        output = tmpl.render(METADATA, "library", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert "generated_at" in data

    def test_author_override(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="json", author="Bob")
        data = json.loads(output)
        assert data["author"] == "Bob"

    def test_license_override(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="json", license_id="Apache-2.0")
        data = json.loads(output)
        assert data["license"] == "Apache-2.0"


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

class TestMarkdownOutput:
    def test_contains_h1_with_name(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert output.startswith("# my-python-tool")

    def test_contains_version_in_header(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "v1.2.3" in output

    def test_contains_description(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "handy Python utility" in output

    def test_contains_installation_section(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "## Installation" in output

    def test_contains_usage_section(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "## Usage" in output

    def test_contains_features_section(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "## Features" in output

    def test_contains_requirements_section(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "## Requirements" in output

    def test_features_as_bullet_points(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "- Fast parsing" in output

    def test_install_command_in_code_block(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "pip install my-python-tool" in output

    def test_keywords_as_inline_code(self, tmpl):
        output = tmpl.render(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "`python`" in output


# ---------------------------------------------------------------------------
# Tool-type specific installation commands
# ---------------------------------------------------------------------------

class TestInstallationByToolType:
    def test_python_cli(self, tmpl):
        out = tmpl.render(METADATA, "cli", [], output_format="json")
        data = json.loads(out)
        assert "pip install" in data["installation"]

    def test_github_action(self, tmpl):
        meta = {**METADATA, "repository": "alice/my-action"}
        out = tmpl.render(meta, "github-action", [], output_format="json")
        data = json.loads(out)
        assert "uses:" in data["installation"]

    def test_javascript_global_cli(self, tmpl):
        meta = {**METADATA, "language": "JavaScript"}
        out = tmpl.render(meta, "cli", [], output_format="json")
        data = json.loads(out)
        assert "npm install -g" in data["installation"]

    def test_javascript_library(self, tmpl):
        meta = {**METADATA, "language": "JavaScript"}
        out = tmpl.render(meta, "library", [], output_format="json")
        data = json.loads(out)
        assert "npm install" in data["installation"]
        assert "-g" not in data["installation"]

    def test_rust_tool(self, tmpl):
        meta = {**METADATA, "language": "Rust"}
        out = tmpl.render(meta, "cli", [], output_format="json")
        data = json.loads(out)
        assert "cargo install" in data["installation"]


# ---------------------------------------------------------------------------
# Usage examples by tool type
# ---------------------------------------------------------------------------

class TestUsageByToolType:
    def test_cli_with_commands(self, tmpl):
        meta = {**METADATA, "cli_commands": ["my-python-tool"]}
        out = tmpl.render(meta, "cli", [], output_format="json")
        data = json.loads(out)
        assert "--help" in data["usage"]

    def test_mcp_server(self, tmpl):
        out = tmpl.render(METADATA, "mcp-server", [], output_format="json")
        data = json.loads(out)
        assert "--help" in data["usage"]

    def test_library_python_import(self, tmpl):
        out = tmpl.render(METADATA, "library", [], output_format="json")
        data = json.loads(out)
        assert "import" in data["usage"] or "from" in data["usage"]


# ---------------------------------------------------------------------------
# render_full_listing (backwards compat)
# ---------------------------------------------------------------------------

class TestRenderFullListing:
    def test_returns_yaml_by_default(self, tmpl):
        output = tmpl.render_full_listing(METADATA, "cli", KEYWORDS)
        assert "name:" in output

    def test_json_format(self, tmpl):
        output = tmpl.render_full_listing(METADATA, "cli", KEYWORDS, output_format="json")
        data = json.loads(output)
        assert data["name"] == "my-python-tool"

    def test_markdown_format(self, tmpl):
        output = tmpl.render_full_listing(METADATA, "cli", KEYWORDS, output_format="markdown")
        assert "# my-python-tool" in output


# ---------------------------------------------------------------------------
# TOOL_TYPES constant
# ---------------------------------------------------------------------------

class TestToolTypes:
    def test_expected_types_present(self):
        for t in ("cli", "library", "web-app", "service", "plugin", "mcp-server", "github-action"):
            assert t in TOOL_TYPES
