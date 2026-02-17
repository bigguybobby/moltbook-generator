"""
Repository Parsers

Parse various project configuration files to extract metadata:
- package.json (Node.js/npm)
- pyproject.toml (Python)
- Cargo.toml (Rust)
- README.md
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import toml
except ImportError:
    toml = None

try:
    import yaml
except ImportError:
    yaml = None


class RepoParser:
    """Parse repository metadata from various config files."""

    def parse(self, repo_path: Path) -> Dict[str, Any]:
        """
        Parse a repository and extract all available metadata.

        Args:
            repo_path: Path to the repository root

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            "name": repo_path.name,
            "description": "",
            "version": "",
            "language": "",
            "dependencies": [],
            "features": [],
            "readme_excerpt": "",
            "has_bin": False,
            "cli_commands": [],
            "has_web_framework": False,
            "has_server": False,
            "has_daemon": False,
        }

        # Try parsing different config files
        if (repo_path / "package.json").exists():
            self._parse_package_json(repo_path, metadata)

        if (repo_path / "pyproject.toml").exists():
            self._parse_pyproject(repo_path, metadata)

        if (repo_path / "Cargo.toml").exists():
            self._parse_cargo(repo_path, metadata)

        if (repo_path / "go.mod").exists():
            self._parse_go_mod(repo_path, metadata)

        # Parse README
        readme_path = self._find_readme(repo_path)
        if readme_path:
            self._parse_readme(readme_path, metadata)

        # Detect language if not already set
        if not metadata["language"]:
            metadata["language"] = self._detect_language(repo_path)

        return metadata

    def _parse_package_json(self, repo_path: Path, metadata: Dict[str, Any]):
        """Parse package.json for Node.js projects."""
        try:
            with open(repo_path / "package.json") as f:
                data = json.load(f)

            metadata["name"] = data.get("name", metadata["name"])
            metadata["description"] = data.get("description", "")
            metadata["version"] = data.get("version", "")
            metadata["language"] = "JavaScript"

            # Check for CLI
            if "bin" in data:
                metadata["has_bin"] = True
                if isinstance(data["bin"], dict):
                    metadata["cli_commands"] = list(data["bin"].keys())
                elif isinstance(data["bin"], str):
                    metadata["cli_commands"] = [metadata["name"]]

            # Extract dependencies
            deps = list(data.get("dependencies", {}).keys())
            dev_deps = list(data.get("devDependencies", {}).keys())
            metadata["dependencies"] = deps + dev_deps

            # Detect frameworks
            web_frameworks = {"express", "koa", "fastify", "next", "nuxt", "react", "vue"}
            if any(fw in deps for fw in web_frameworks):
                metadata["has_web_framework"] = True

        except Exception as e:
            pass  # Silently skip parsing errors

    def _parse_pyproject(self, repo_path: Path, metadata: Dict[str, Any]):
        """Parse pyproject.toml for Python projects."""
        if not toml:
            return

        try:
            with open(repo_path / "pyproject.toml") as f:
                data = toml.load(f)

            project = data.get("project", {})
            metadata["name"] = project.get("name", metadata["name"])
            metadata["description"] = project.get("description", "")
            metadata["version"] = project.get("version", "")
            metadata["language"] = "Python"

            # Check for CLI scripts
            if "scripts" in project:
                metadata["has_bin"] = True
                metadata["cli_commands"] = list(project["scripts"].keys())

            # Extract dependencies
            deps = project.get("dependencies", [])
            if isinstance(deps, list):
                metadata["dependencies"] = deps
            elif isinstance(deps, dict):
                metadata["dependencies"] = list(deps.keys())

            # Detect frameworks
            web_frameworks = {"fastapi", "flask", "django", "starlette", "aiohttp"}
            dep_str = " ".join(metadata["dependencies"]).lower()
            if any(fw in dep_str for fw in web_frameworks):
                metadata["has_web_framework"] = True

        except Exception as e:
            pass

    def _parse_cargo(self, repo_path: Path, metadata: Dict[str, Any]):
        """Parse Cargo.toml for Rust projects."""
        if not toml:
            return

        try:
            with open(repo_path / "Cargo.toml") as f:
                data = toml.load(f)

            package = data.get("package", {})
            metadata["name"] = package.get("name", metadata["name"])
            metadata["description"] = package.get("description", "")
            metadata["version"] = package.get("version", "")
            metadata["language"] = "Rust"

            # Check for binary
            if "bin" in data or (repo_path / "src/main.rs").exists():
                metadata["has_bin"] = True
                metadata["cli_commands"] = [metadata["name"]]

            # Extract dependencies
            deps = data.get("dependencies", {})
            metadata["dependencies"] = list(deps.keys())

            # Detect frameworks
            web_frameworks = {"actix-web", "rocket", "axum", "warp"}
            if any(fw in deps for fw in web_frameworks):
                metadata["has_web_framework"] = True

        except Exception as e:
            pass

    def _parse_go_mod(self, repo_path: Path, metadata: Dict[str, Any]):
        """Parse go.mod for Go projects."""
        try:
            with open(repo_path / "go.mod") as f:
                content = f.read()

            # Extract module name
            if match := re.search(r"module\s+(\S+)", content):
                metadata["name"] = match.group(1).split("/")[-1]

            metadata["language"] = "Go"

            # Check for main package
            if (repo_path / "main.go").exists() or (repo_path / "cmd").is_dir():
                metadata["has_bin"] = True
                metadata["cli_commands"] = [metadata["name"]]

        except Exception as e:
            pass

    def _find_readme(self, repo_path: Path) -> Optional[Path]:
        """Find README file (case-insensitive)."""
        for name in ["README.md", "README.MD", "readme.md", "README", "readme.txt"]:
            readme_path = repo_path / name
            if readme_path.exists():
                return readme_path
        return None

    def _parse_readme(self, readme_path: Path, metadata: Dict[str, Any]):
        """Extract key information from README."""
        try:
            content = readme_path.read_text(encoding="utf-8", errors="ignore")

            # Extract first paragraph as excerpt (skip title)
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            excerpt_lines = []

            for line in lines:
                # Skip markdown headers
                if line.startswith("#"):
                    continue
                # Skip badges
                if "badge" in line.lower() or line.startswith("[!["):
                    continue
                # Collect first non-empty paragraph
                if line and not line.startswith("["):
                    excerpt_lines.append(line)
                    if len(" ".join(excerpt_lines)) > 200:
                        break

            metadata["readme_excerpt"] = " ".join(excerpt_lines)[:500]

            # Extract features section
            features = []
            in_features = False

            for line in content.split("\n"):
                lower = line.lower().strip()

                # Detect features section
                if any(
                    heading in lower
                    for heading in ["## features", "## key features", "# features"]
                ):
                    in_features = True
                    continue

                # Stop at next section
                if in_features and line.startswith("#"):
                    break

                # Extract bullet points
                if in_features and (line.strip().startswith("-") or line.strip().startswith("*")):
                    feature = line.strip().lstrip("-*").strip()
                    if feature and len(feature) < 100:
                        features.append(feature)

            metadata["features"] = features[:5]  # Top 5 features

        except Exception as e:
            pass

    def _detect_language(self, repo_path: Path) -> str:
        """Detect primary language from file extensions."""
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".rs": "Rust",
            ".go": "Go",
            ".rb": "Ruby",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
        }

        counts = {}
        for ext, lang in extensions.items():
            count = len(list(repo_path.rglob(f"*{ext}")))
            if count > 0:
                counts[lang] = counts.get(lang, 0) + count

        if counts:
            return max(counts, key=counts.get)

        return "Unknown"
