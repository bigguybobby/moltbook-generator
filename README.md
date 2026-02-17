# MoltBook Listing Generator

Generate optimized MoltBook format listings from GitHub repositories automatically.

## Features

- 🔍 **Auto-parse** package.json, pyproject.toml, Cargo.toml, go.mod, and README.md
- 🤖 **AI-powered descriptions** using Claude for compelling, concise descriptions
- 🏷️ **Smart keyword extraction** from dependencies and project content
- 📦 **Multi-language support** Python, JavaScript/TypeScript, Rust, Go, and more
- 🎯 **Auto-detect tool type** CLI, library, web app, service, or plugin
- 👁️ **Preview mode** to review before saving
- ⚡ **Fast** shallow cloning and efficient parsing

## Installation

```bash
# Install from source
cd ~/projects/near-market/moltbook-generator
pip install -e .

# Or with Poetry
poetry install
```

## Usage

### Basic Usage

```bash
# Generate from GitHub URL
moltbook-gen https://github.com/user/awesome-tool

# Generate from local directory
moltbook-gen ./my-project

# Preview without saving
moltbook-gen https://github.com/user/repo --preview

# Specify output file
moltbook-gen https://github.com/user/repo -o custom-name.yaml
```

### Advanced Options

```bash
# Skip AI enhancement (faster, no API key needed)
moltbook-gen https://github.com/user/repo --no-ai

# Override tool type detection
moltbook-gen https://github.com/user/repo --tool-type cli

# Verbose output for debugging
moltbook-gen https://github.com/user/repo -v
```

### Using with API Key

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

# Or pass directly
moltbook-gen https://github.com/user/repo --api-key sk-ant-...
```

## Configuration

MoltBook Generator parses these config files (in order of priority):

1. **Node.js/npm** - `package.json`
2. **Python** - `pyproject.toml`
3. **Rust** - `Cargo.toml`
4. **Go** - `go.mod`
5. **Documentation** - `README.md`

## Output Format

Generates YAML in MoltBook format:

```yaml
# MoltBook Listing
# Generated: 2026-02-16 12:19:00
# Tool: awesome-tool

name: awesome-tool
version: 1.2.3
type: cli
language: Python
keywords:
  - cli
  - automation
  - python

description: "A powerful CLI tool for automating development workflows with intelligent task detection."

features:
  - Fast and efficient task execution
  - Plugin system for extensibility
  - Cross-platform support

installation: "pip install awesome-tool"

usage: "awesome-tool --help"

requirements: "Python >= 3.9"
```

## Examples

See the `examples/` directory for sample outputs:

```bash
# Generate example listings
cd examples
moltbook-gen https://github.com/astral-sh/ruff
moltbook-gen https://github.com/vercel/next.js
moltbook-gen https://github.com/tokio-rs/tokio
```

## Development

### Setup

```bash
# Clone and install
git clone https://github.com/near-market/moltbook-generator.git
cd moltbook-generator
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

### Project Structure

```
moltbook-generator/
├── src/moltbook_generator/
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI interface with argparse
│   ├── generator.py         # Core generation logic
│   ├── parsers.py           # Config file parsers
│   └── templates.py         # MoltBook YAML templates
├── examples/                # Example outputs
├── tests/                   # Test suite
├── pyproject.toml           # Project config
└── README.md
```

## Dependencies

- **requests** - HTTP client for API calls
- **pyyaml** - YAML generation
- **toml** - Parse TOML config files
- **anthropic** - Claude API for AI descriptions
- **gitpython** - Clone GitHub repositories

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

- 📧 Issues: https://github.com/near-market/moltbook-generator/issues
- 💬 Discussions: https://github.com/near-market/moltbook-generator/discussions

---

Made with ❤️ for the MoltBook ecosystem
