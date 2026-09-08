# Seinpy

Welcome to **`seinpy`**, an extensible Python tool to build and programmatically access data on Seinfeld scripts! `seinpy` can be used to analyze character dialogues, study the structure of episodes, or extract ratingand credits information.

![seinpy](assets/seinpy.png)

## Key Features

- **Extensible Script Extraction**: Programmatically download, parse, and structure scripts.
- **Metadata Integration**: Optionally pull episode ratings and credits from OMDb.
- **Export Formats**: Export structured Seinfeld data into standard formats for analysis.
- **Built for Polars**: Leverages Polars DataFrames for fast and efficient analytical queries.

## Getting Started

To install `seinpy` and set up your environment, follow the steps below:

### Installation

`seinpy` is deployed to PyPI and can be installed with `pip`:

```bash
pip install seinpy
```

### Quick Usage

Here is a quick example of how to load episode data:

```python
from seinpy import read_episodes, write_episodes, Source

# Configure sources
source = Source(script="kaggle")

# Read scripts
episodes = read_episodes(source=source, get_all=True)

# Export the episodes into a single JSON file
write_episodes(
    save_type="json",
    save_path="seinfeld_episodes.json",
    data=episodes,
)
```

## Documentation Sections

Explore different parts of the documentation:

* **[Installation](installation.md)**: Installation and configuration instructions.
* **[Reference](reference.md)**: Details about the project background, usage options, and internal architecture.
* **[Examples](examples.md)**: Practical examples and tutorials on what you can do with `seinpy`.
* **[API Reference](api.md)**: Complete API documentation extracted from the source code.
* **[Contributing](contributing.md)**: Information on how to contribute to `seinpy`.
