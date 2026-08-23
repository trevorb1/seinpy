# Seinpy

Welcome to **seinpy**, an extensible Python tool to build and programmatically access data on Seinfeld scripts!

Whether you want to analyze character dialogues, study the structure of episodes, or extract ratings and credits information, `seinpy` provides a clean, Pythonic interface to load, parse, and export Seinfeld episode data.

## Key Features

- **Extensible Script Extraction**: Programmatically download, parse, and structure scripts.
- **Rich Metadata Integration**: Optionally pull episode ratings and credits from OMDb.
- **Export Formats**: Export structured Seinfeld data into standard formats for analysis.
- **Built for Polars**: Leverages Polars DataFrames for fast and efficient analytical queries.

## Getting Started

To install `seinpy` and set up your environment, follow the steps below:

### Installation

`seinpy` uses [uv](https://astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/trevorb1/seinpy.git
cd seinpy

# Install dependencies and sync the environment
uv sync
```

### Quick Usage

Here is a quick example of how to load episode data:

```python
from seinpy import read_episodes, Source

# Configure the Kaggle source for scripts
source = Source(script="kaggle")

# Load all episodes into memory
episodes = read_episodes(source=source, get_all=True)
print(f"Loaded {len(episodes)} episodes!")
```

## Documentation Sections

Explore different parts of the documentation:

* **[Reference](reference.md)**: Details about the project background, usage options, and internal architecture.
* **[Examples](examples.md)**: Practical examples and tutorials on what you can do with `seinpy`.
* **[API Reference](api.md)**: Complete API documentation extracted from the source code.
